from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User, Transaction
from app.schemas.receipt import ReceiptResponse, ReceiptAnalysis, ReceiptProcessingResponse, ReceiptError
from app.services.receipt_processor import ReceiptProcessor
from app.services.ai_categorization import TransactionCategorizer, categorize_transaction

router = APIRouter()
receipt_processor = ReceiptProcessor()
categorizer = TransactionCategorizer()

@router.post("/process", response_model=ReceiptResponse)
async def process_receipt(
    receipt: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a receipt image and extract information
    """
    try:
        # Read image content
        image_bytes = await receipt.read()
        
        # Enhance image quality
        enhanced_image = receipt_processor.enhance_image(image_bytes)
        
        # Process receipt
        result = receipt_processor.process_receipt(enhanced_image)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Receipt processing failed: {result.get('error', 'Unknown error')}"
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing receipt: {str(e)}"
        )

@router.post("/analyze", response_model=ReceiptAnalysis)
async def analyze_receipt(
    receipt: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process receipt and provide AI analysis
    """
    try:
        # First process the receipt
        image_bytes = await receipt.read()
        enhanced_image = receipt_processor.enhance_image(image_bytes)
        result = receipt_processor.process_receipt(enhanced_image)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Receipt processing failed: {result.get('error', 'Unknown error')}"
            )
        
        receipt_data = result["data"]
        
        # Get category prediction
        merchant_desc = receipt_data["merchant"] or ""
        amount = receipt_data["amount"] or 0.0
        prediction = categorizer.predict_category(
            description=merchant_desc,
            amount=amount
        )
        
        # Get similar transactions
        similar_transactions = []
        if prediction["category"] != "Other":
            transactions = db.query(Transaction).filter(
                Transaction.user_id == current_user.id,
                Transaction.category_id == prediction["category"]
            ).limit(3).all()
            similar_transactions = [t.description for t in transactions]
        
        return ReceiptAnalysis(
            receipt_data=receipt_data,
            suggested_category=prediction["category"],
            confidence_score=prediction["confidence"],
            similar_transactions=similar_transactions,
            budget_impact=amount
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing receipt: {str(e)}"
        )

@router.post("/create-transaction")
async def create_transaction_from_receipt(
    receipt: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process receipt and create a transaction
    """
    try:
        # First analyze the receipt
        image_bytes = await receipt.read()
        enhanced_image = receipt_processor.enhance_image(image_bytes)
        result = receipt_processor.process_receipt(enhanced_image)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Receipt processing failed: {result.get('error', 'Unknown error')}"
            )
        
        receipt_data = result["data"]
        
        # Get category prediction
        merchant_desc = receipt_data["merchant"] or ""
        amount = receipt_data["amount"] or 0.0
        prediction = categorizer.predict_category(
            description=merchant_desc,
            amount=amount
        )
        
        # Create transaction
        transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            description=merchant_desc,
            date=receipt_data["date"],
            category_id=prediction["category"],
            receipt_url=None  # TODO: Implement receipt storage
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return {
            "message": "Transaction created successfully",
            "transaction_id": transaction.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating transaction: {str(e)}"
        )

@router.post("/upload", response_model=ReceiptProcessingResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    create_transaction: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a receipt image.
    Optionally create a transaction from the receipt data.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image file
        contents = await file.read()
        
        # Process receipt
        result = await receipt_processor.process_image(contents)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # If requested, create a transaction from the receipt
        if create_transaction and result["total_amount"]:
            description = f"Receipt from {result['merchant'] or 'Unknown Merchant'}"
            
            # Use AI to categorize the transaction
            category = await categorize_transaction(description, result["total_amount"])
            
            # Create transaction
            transaction = Transaction(
                amount=result["total_amount"],
                description=description,
                category=category,
                user_id=current_user.id,
                date=result["date"]
            )
            db.add(transaction)
            db.commit()
        
        return ReceiptProcessingResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 