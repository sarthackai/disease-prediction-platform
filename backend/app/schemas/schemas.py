"""
schemas.py
Pydantic models defining the shape of API request and response data.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# ------------------------------------------------------------------
# AUTH SCHEMAS
# ------------------------------------------------------------------
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    full_name: str
    role: str

# ------------------------------------------------------------------
# PREDICTION SCHEMAS
# ------------------------------------------------------------------
class PredictionRequest(BaseModel):
    symptoms: List[str]  # list of symptom names the user selected
    input_method: Optional[str] = "manual"

class TopPrediction(BaseModel):
    disease: str
    probability: float

class ShapEntry(BaseModel):
    symptom: str
    shap_value: float

class PredictionResponse(BaseModel):
    prediction_id: str
    predicted_disease: str
    confidence_score: float
    severity_level: str
    top_predictions: List[TopPrediction]
    shap_explanation: List[ShapEntry]
    prevention_tips: List[str]
    specialist_type: str
    model_used: str

# ------------------------------------------------------------------
# HOSPITAL SCHEMAS
# ------------------------------------------------------------------
class HospitalResponse(BaseModel):
    hospital_id: str
    name: str
    latitude: float
    longitude: float
    address: Optional[str]
    phone: Optional[str]
    rating: Optional[float]
    specialties: Optional[List[str]]
    distance_km: Optional[float]

# ------------------------------------------------------------------
# MEDICAL HISTORY SCHEMAS
# ------------------------------------------------------------------
class HistoryItem(BaseModel):
    prediction_id: str
    predicted_disease: str
    confidence_score: float
    symptoms_input: Dict[str, Any]
    created_at: datetime
    pdf_url: Optional[str]

# ------------------------------------------------------------------
# PROFILE SCHEMAS
# ------------------------------------------------------------------
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None