# AI-Powered Personal Finance Manager

A comprehensive personal finance management system with AI-powered features for transaction categorization and receipt processing.

## Features

- User authentication with password reset
- Transaction management
- AI-powered transaction categorization
- Receipt processing with OCR
- Data visualization
- Export functionality (CSV, Excel, JSON)
- Mobile-responsive design

## Tech Stack

### Backend
- FastAPI
- SQLite
- SQLAlchemy
- OpenAI
- Tesseract OCR

### Frontend
- React
- Material-UI
- Recharts
- TypeScript

## Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file:
```bash
cp .env.example .env
```

5. Run migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create .env file:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend
- `DATABASE_URL`: SQLite database URL
- `SECRET_KEY`: JWT secret key
- `OPENAI_API_KEY`: OpenAI API key
- `SMTP_*`: Email configuration

### Frontend
- `VITE_API_URL`: Backend API URL

=
