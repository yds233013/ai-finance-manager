from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReceiptItem(BaseModel):
    description: str
    amount: float

class ReceiptProcessingResponse(BaseModel):
    date: Optional[str]
    total_amount: Optional[float]
    items: List[ReceiptItem]
    merchant: Optional[str]
    raw_text: str

class ReceiptError(BaseModel):
    error: str
    details: Optional[str]

class ReceiptData(BaseModel):
    amount: Optional[float]
    date: Optional[str]
    merchant: Optional[str]
    raw_text: str

class ReceiptResponse(BaseModel):
    success: bool
    data: Optional[ReceiptData] = None
    error: Optional[str] = None

class ReceiptAnalysis(BaseModel):
    receipt_data: ReceiptData
    suggested_category: str
    confidence_score: float
    similar_transactions: list[str] = []
    budget_impact: Optional[float] = None 