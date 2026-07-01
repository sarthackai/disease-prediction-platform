# 🏥 HealthAI — AI-Powered Disease Prediction and Hospital Recommendation System

> AI/ML Project | Good Health and Well-Being

[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://reactjs.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-97.6%25_Accuracy-orange)](https://xgboost.readthedocs.io)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Project Overview

HealthAI is a full-stack, production-ready AI healthcare platform that:

- Accepts symptoms from users via an interactive checklist
- Predicts diseases using trained Machine Learning models
- Explains predictions using SHAP Explainable AI
- Recommends nearby hospitals via live OpenStreetMap integration
- Generates downloadable PDF medical reports
- Stores complete medical history per user
- Secured with JWT authentication and Supabase Row Level Security

---

## 🖥️ Live Demo

| Page | Description |
|------|-------------|
| Landing Page | Project overview and entry point |
| Register / Login | JWT-secured authentication |
| Dashboard | User home with quick actions |
| Symptom Input | 132-symptom searchable checklist |
| Prediction Result | Disease prediction + SHAP explanation |
| Hospital Finder | Live map with nearby hospitals |
| Medical History | All past predictions |
| PDF Report | Downloadable clinical report |

---

## 🤖 Machine Learning

### Dataset
- **Source:** Kaggle — Disease Prediction Using Machine Learning (kaushil268)
- **Training records:** 4,920
- **Testing records:** 42
- **Symptom features:** 132 binary symptom indicators
- **Disease classes:** 41

### Model Comparison

| Model | Accuracy | Precision | Recall | F1 Score |
|-------|----------|-----------|--------|----------|
| Random Forest | 97.6% | 98.78% | 98.78% | 98.37% |
| XGBoost | 97.6% | 98.78% | 98.78% | 98.37% |

**Selected Model:** XGBoost (tiebreaker — faster inference, lower memory footprint)

### Explainable AI
- SHAP (SHapley Additive exPlanations) used to explain every prediction
- Shows top 5 symptoms that influenced the AI decision
- Green = pushed toward predicted disease
- Red = pushed away from predicted disease

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React + TypeScript | UI framework |
| Tailwind CSS | Styling |
| React Router | Navigation |
| Axios | API calls |
| React Leaflet | Hospital map |
| Recharts | Data visualization |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| Python 3.14 | Backend language |
| JWT (python-jose) | Authentication |
| bcrypt | Password hashing |
| ReportLab | PDF generation |
| httpx | Async HTTP client |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| Scikit-learn | Random Forest + preprocessing |
| XGBoost | Gradient boosting classifier |
| SHAP | Explainable AI |
| Pandas + NumPy | Data processing |
| Joblib | Model serialization |

### Database & Infrastructure
| Technology | Purpose |
|------------|---------|
| Supabase (PostgreSQL) | Cloud database |
| Row Level Security | Data privacy |
| OpenStreetMap + Overpass API | Hospital data |
| Haversine Formula | Distance calculation |

---

## 📁 Project Structure

disease-prediction-platform/
├── frontend/                  # React TypeScript frontend
│   └── src/
│       ├── pages/             # All page components
│       ├── lib/               # API client
│       └── App.tsx            # Router
├── backend/                   # FastAPI backend
│   └── app/
│       ├── api/v1/            # Route handlers
│       ├── core/              # Config, security, Supabase
│       ├── ml/                # Inference + SHAP
│       ├── schemas/           # Pydantic models
│       └── services/          # PDF, hospitals
├── ml-training/               # ML training pipeline
│   ├── data/raw/              # Kaggle CSV files
│   ├── train.py               # Training script
│   └── model_registry/        # Comparison report
├── database/
│   └── migrations/            # SQL schema
└── .antigravity/              # Antigravity workflows

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account (free tier works)

### 1. Clone the repository
```bash
git clone https://github.com/sarthackai/disease-prediction-platform.git
cd disease-prediction-platform
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in your Supabase URL and keys
```

### 3. Set up the database
- Go to your Supabase project
- Open SQL Editor
- Run `database/migrations/0001_init_schema.sql`

### 4. Download the dataset
- Download from [Kaggle](https://www.kaggle.com/datasets/kaushil268/disease-prediction-using-machine-learning)
- Place `Training.csv` and `Testing.csv` in `ml-training/data/raw/`

### 5. Train the ML model
```bash
cd ml-training
python -m venv venv
.\venv\Scripts\activate      # Windows
pip install pandas numpy scikit-learn xgboost shap joblib
python train.py
```

### 6. Start the backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 7. Start the frontend
```bash
cd frontend
npm install
npm start
```

### 8. Open the app
http://localhost:3000

---

## 📊 Database Schema

7 tables with Row Level Security:

| Table | Purpose |
|-------|---------|
| users | Patient accounts |
| predictions | Disease prediction records |
| diseases | Disease metadata + prevention tips |
| hospitals | Hospital cache from OpenStreetMap |
| appointments | Hospital appointments |
| medical_reports | PDF report metadata |
| analytics | Admin dashboard metrics |

---

## 🔐 Security Features

- JWT token authentication (24-hour expiry)
- bcrypt password hashing
- Supabase Row Level Security (users see only their own data)
- Service role key never exposed to frontend
- CORS restricted to localhost in development

---

## 📄 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT |
| GET | `/api/v1/predictions/symptoms` | Get all 132 symptoms |
| POST | `/api/v1/predictions/predict` | Predict disease |
| GET | `/api/v1/predictions/history` | Get user history |
| GET | `/api/v1/hospitals/nearby` | Get nearby hospitals |
| GET | `/api/v1/reports/generate/{id}` | Download PDF report |

Full interactive API docs available at `http://localhost:8000/docs`

---

## 👨‍💻 Author

**Sarthak**
- GitHub: [@sarthackai](https://github.com/sarthackai)
- Project: AI/ML

---

## 📜 License

This project is licensed under the MIT License.

---

##  Acknowledgements

- Dataset: [kaushil268 on Kaggle](https://www.kaggle.com/datasets/kaushil268/disease-prediction-using-machine-learning)
- Maps: [OpenStreetMap Contributors](https://www.openstreetmap.org)
- Icons: [Lucide React](https://lucide.dev)
- UI Components: [ShadCN UI](https://ui.shadcn.com)

---