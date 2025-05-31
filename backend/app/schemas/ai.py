from pydantic import BaseModel
from typing import List, Optional

class BudgetSuggestion(BaseModel):
    suggestions: List[str]
    analysis: str

class CategoryPrediction(BaseModel):
    category: str
    confidence: float

class TransactionAnalysis(BaseModel):
    predicted_category: CategoryPrediction
    similar_transactions: Optional[List[str]] = None
    spending_trend: Optional[str] = None
    budget_impact: Optional[float] = None

class BudgetRecommendation(BaseModel):
    category: str
    current_spending: float
    recommended_limit: float
    explanation: str

class AIResponse(BaseModel):
    success: bool
    message: str
    data: dict = {} 