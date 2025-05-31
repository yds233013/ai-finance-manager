from fastapi import APIRouter
from app.api.endpoints import users, auth, transactions, receipts, export

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(export.router, prefix="/export", tags=["export"]) 