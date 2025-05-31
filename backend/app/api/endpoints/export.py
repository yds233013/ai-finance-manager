from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime
import csv
import io
import json
import pandas as pd
from app.core.security import get_current_user
from app.models.user import User
from app.crud.transaction import get_user_transactions
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/transactions/csv")
async def export_transactions_csv(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    categories: List[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions as CSV"""
    transactions = get_user_transactions(
        db, current_user.id, start_date, end_date, categories
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Description', 'Amount', 'Category'])
    
    # Write transactions
    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.description,
            transaction.amount,
            transaction.category
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@router.get("/transactions/excel")
async def export_transactions_excel(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    categories: List[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions as Excel"""
    transactions = get_user_transactions(
        db, current_user.id, start_date, end_date, categories
    )
    
    # Convert to pandas DataFrame
    df = pd.DataFrame([{
        'Date': t.date,
        'Description': t.description,
        'Amount': t.amount,
        'Category': t.category
    } for t in transactions])
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Transactions']
        
        # Add formats
        money_fmt = workbook.add_format({'num_format': '$#,##0.00'})
        date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        
        # Apply formats to columns
        worksheet.set_column('A:A', 12, date_fmt)  # Date
        worksheet.set_column('B:B', 30)  # Description
        worksheet.set_column('C:C', 12, money_fmt)  # Amount
        worksheet.set_column('D:D', 15)  # Category
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )

@router.get("/transactions/json")
async def export_transactions_json(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    categories: List[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions as JSON"""
    transactions = get_user_transactions(
        db, current_user.id, start_date, end_date, categories
    )
    
    # Convert transactions to dict
    transactions_data = [{
        'date': t.date.isoformat() if t.date else None,
        'description': t.description,
        'amount': t.amount,
        'category': t.category
    } for t in transactions]
    
    return StreamingResponse(
        iter([json.dumps(transactions_data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.json"}
    ) 