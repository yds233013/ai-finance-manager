from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import User, Transaction, Category
from app.schemas.transaction import (
    Transaction as TransactionSchema,
    TransactionCreate,
    TransactionUpdate,
    TransactionWithCategory,
    TransactionResponse
)
from app.services.ai_categorization import categorize_transaction, suggest_budget_improvements
from app.schemas.ai import AIResponse

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use AI to categorize the transaction
    category = await categorize_transaction(transaction.description, transaction.amount)
    
    db_transaction = Transaction(
        amount=transaction.amount,
        description=transaction.description,
        category=category,
        user_id=current_user.id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return transactions

@router.get("/{transaction_id}", response_model=TransactionWithCategory)
def read_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get transaction by ID.
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction

@router.put("/{transaction_id}", response_model=TransactionSchema)
def update_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    transaction_in: TransactionUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update transaction.
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    for field, value in transaction_in.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}")
def delete_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete transaction.
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    return {"status": "success"}

@router.get("/analysis", response_model=AIResponse)
async def get_budget_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    if not transactions:
        return AIResponse(
            success=True,
            message="No transactions found for analysis",
            data={"suggestions": []}
        )
    
    # Convert transactions to list of dicts for AI analysis
    transaction_data = [
        {"amount": t.amount, "category": t.category, "description": t.description}
        for t in transactions
    ]
    
    suggestions = await suggest_budget_improvements(transaction_data)
    
    return AIResponse(
        success=True,
        message="Budget analysis completed",
        data={
            "suggestions": suggestions.split("\n"),
            "transaction_count": len(transactions)
        }
    ) 