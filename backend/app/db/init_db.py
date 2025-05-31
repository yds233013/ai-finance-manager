from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Base, Category
from app.db.session import engine

# Create default categories
DEFAULT_CATEGORIES = [
    "Food & Dining",
    "Shopping",
    "Transportation",
    "Bills & Utilities",
    "Entertainment",
    "Health & Fitness",
    "Travel",
    "Education",
    "Gifts & Donations",
    "Investments",
    "Other"
]

def init_db() -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)

def create_default_categories(db: Session) -> None:
    # Check if categories already exist
    existing_categories = db.query(Category).all()
    if not existing_categories:
        for category_name in DEFAULT_CATEGORIES:
            category = Category(
                name=category_name,
                description=f"Default category for {category_name} expenses"
            )
            db.add(category)
        db.commit()

if __name__ == "__main__":
    init_db() 