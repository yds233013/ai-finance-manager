from typing import List, Dict
import openai
from app.core.config import settings
import re

CATEGORY_DESCRIPTIONS = {
    "food": "Restaurants, groceries, and food delivery",
    "transportation": "Public transit, fuel, car maintenance, ride-sharing",
    "shopping": "Clothing, electronics, home goods",
    "entertainment": "Movies, games, streaming services, hobbies",
    "utilities": "Electricity, water, gas, internet, phone",
    "housing": "Rent, mortgage, repairs, furniture",
    "healthcare": "Medical bills, medications, insurance",
    "education": "Tuition, books, courses, training",
    "travel": "Flights, hotels, vacation expenses",
    "other": "Miscellaneous expenses"
}

class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            "food_dining": {
                "name": "Food & Dining",
                "keywords": ["restaurant", "cafe", "coffee", "food", "grocery", "meal", "uber eats", "doordash"]
            },
            "shopping": {
                "name": "Shopping",
                "keywords": ["amazon", "walmart", "target", "store", "shop", "retail", "clothing"]
            },
            "transportation": {
                "name": "Transportation",
                "keywords": ["uber", "lyft", "taxi", "bus", "train", "subway", "gas", "parking"]
            },
            "bills_utilities": {
                "name": "Bills & Utilities",
                "keywords": ["electricity", "water", "gas", "internet", "phone", "utility", "bill"]
            },
            "entertainment": {
                "name": "Entertainment",
                "keywords": ["movie", "theatre", "concert", "netflix", "spotify", "game", "streaming"]
            },
            "health_fitness": {
                "name": "Health & Fitness",
                "keywords": ["gym", "doctor", "medical", "pharmacy", "fitness", "health"]
            },
            "travel": {
                "name": "Travel",
                "keywords": ["hotel", "flight", "airline", "airbnb", "travel", "vacation"]
            },
            "education": {
                "name": "Education",
                "keywords": ["school", "university", "college", "course", "book", "tuition"]
            }
        }
        
        # Compile regex patterns for each category
        self.patterns = {
            category: re.compile('|'.join(r'\b{}\b'.format(k.lower()) for k in info['keywords']), re.IGNORECASE)
            for category, info in self.categories.items()
        }
        
        # Initialize TF model (placeholder for now)
        self.model = None
        
    def predict_category(self, description: str, amount: float) -> Dict:
        """
        Predict category for a transaction based on description and amount
        """
        if not description:
            return {"category": "other", "confidence": 0.0}
        
        # Initialize scores
        scores = {category: 0 for category in self.categories.keys()}
        
        # Check for keyword matches
        for category, pattern in self.patterns.items():
            matches = pattern.findall(description.lower())
            if matches:
                scores[category] = len(matches)
        
        # Get category with highest score
        max_score = max(scores.values())
        if max_score == 0:
            return {"category": "other", "confidence": 0.0}
        
        # Get category with highest score
        best_category = max(scores.items(), key=lambda x: x[1])[0]
        confidence = min(max_score / 3, 1.0)  # Normalize confidence
        
        return {
            "category": self.categories[best_category]["name"],
            "confidence": confidence
        }

    def get_similar_transactions(self, transactions: List[Dict], target: Dict) -> List[Dict]:
        """
        Find similar transactions based on description and amount
        """
        similar = []
        target_category = self.predict_category(target["description"], target["amount"])["category"]
        
        for transaction in transactions:
            if transaction["id"] == target["id"]:
                continue
            
            category = self.predict_category(transaction["description"], transaction["amount"])["category"]
            if category == target_category:
                similar.append(transaction)
        
        return similar[:3]  # Return top 3 similar transactions
    
    def train_model(self, training_data: List[Dict]):
        """
        Train the ML model with historical transaction data.
        To be implemented in the future.
        """
        pass 

async def categorize_transaction(description: str, amount: float) -> str:
    """
    Use AI to categorize a transaction based on its description and amount.
    """
    try:
        prompt = f"""
        Given the following transaction:
        Description: {description}
        Amount: ${amount}
        
        Categorize this transaction into one of these categories:
        {', '.join(CATEGORY_DESCRIPTIONS.keys())}
        
        Category descriptions:
        {chr(10).join([f'- {k}: {v}' for k, v in CATEGORY_DESCRIPTIONS.items()])}
        
        Return only the category name, nothing else.
        """
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=10,
            temperature=0.3
        )
        
        category = response.choices[0].text.strip().lower()
        return category if category in CATEGORY_DESCRIPTIONS else "other"
        
    except Exception as e:
        print(f"Error in AI categorization: {e}")
        return "other"

async def suggest_budget_improvements(transactions: List[Dict]) -> str:
    """
    Analyze transaction patterns and suggest budget improvements.
    """
    try:
        # Prepare transaction summary
        categories = {}
        for t in transactions:
            cat = t.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(t['amount'])
        
        summary = "Transaction Summary:\n"
        for cat, amounts in categories.items():
            total = sum(amounts)
            count = len(amounts)
            avg = total / count
            summary += f"{cat}: ${total:.2f} total, {count} transactions, ${avg:.2f} average\n"
        
        prompt = f"""
        {summary}
        
        Based on this spending pattern, provide 3 specific suggestions for budget improvement.
        Focus on practical ways to reduce expenses and optimize spending.
        Keep the response concise and actionable.
        """
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].text.strip()
        
    except Exception as e:
        print(f"Error in budget analysis: {e}")
        return "Unable to generate budget suggestions at this time." 