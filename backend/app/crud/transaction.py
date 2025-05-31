from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from typing import List, Optional

def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user_id).offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def create_transaction(db: Session, user_id: int, amount: float, description: str, date: str, category_id: Optional[int] = None) -> Transaction:
    db_transaction = Transaction(
        user_id=user_id,
        amount=amount,
        description=description,
        date=date,
        category_id=category_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction 