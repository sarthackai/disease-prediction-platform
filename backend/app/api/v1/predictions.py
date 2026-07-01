"""
predictions.py
Handles disease prediction requests.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import PredictionRequest, PredictionResponse
from app.core.security import get_current_user
from app.core.supabase_client import supabase
from app.ml.inference import predict_disease, feature_columns, label_encoder
from app.ml.explainability import get_shap_explanation
import numpy as np

router = APIRouter()

# Severity mapping based on disease name keywords
SEVERITY_MAP = {
    "critical": ["heart attack", "stroke", "paralysis", "pneumonia"],
    "high": ["diabetes", "tuberculosis", "malaria", "dengue", "hepatitis"],
    "moderate": ["gastroenteritis", "arthritis", "migraine", "hypothyroidism"],
    "low": ["common cold", "allergy", "acne", "fungal infection"]
}

def get_severity(disease_name: str) -> str:
    disease_lower = disease_name.lower()
    for severity, keywords in SEVERITY_MAP.items():
        if any(keyword in disease_lower for keyword in keywords):
            return severity
    return "moderate"

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    data: PredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    if not data.symptoms:
        raise HTTPException(status_code=400, detail="No symptoms provided")

    # Run ML prediction
    result = predict_disease(data.symptoms)

    # Get predicted class index for SHAP
    predicted_class_index = list(label_encoder.classes_).index(
        result["predicted_disease"]
    )

    # Get SHAP explanation
    shap_explanation = get_shap_explanation(
        result["input_vector"],
        feature_columns,
        predicted_class_index
    )

    # Get disease metadata from Supabase
    disease_data = supabase.table("diseases")\
        .select("*")\
        .eq("disease_name", result["predicted_disease"])\
        .execute()

    prevention_tips = []
    specialist_type = "General Physician"
    if disease_data.data:
        d = disease_data.data[0]
        prevention_tips = d.get("prevention_tips") or []
        specialist_type = d.get("specialist_type") or "General Physician"

    severity_level = get_severity(result["predicted_disease"])

    # Save prediction to Supabase
    saved = supabase.table("predictions").insert({
        "user_id": current_user["sub"],
        "symptoms_input": result["symptoms_input"],
        "confidence_score": result["confidence_score"],
        "severity_score": 0.8 if severity_level == "critical" else
                          0.6 if severity_level == "high" else
                          0.4 if severity_level == "moderate" else 0.2,
        "top_predictions": result["top_predictions"],
        "shap_explanation": shap_explanation,
        "model_used": result["model_used"],
        "model_version": result["model_version"],
        "input_method": data.input_method
    }).execute()

    prediction_id = saved.data[0]["prediction_id"]

    return PredictionResponse(
        prediction_id=prediction_id,
        predicted_disease=result["predicted_disease"],
        confidence_score=result["confidence_score"],
        severity_level=severity_level,
        top_predictions=result["top_predictions"],
        shap_explanation=shap_explanation,
        prevention_tips=prevention_tips,
        specialist_type=specialist_type,
        model_used=result["model_used"]
    )

@router.get("/symptoms")
async def get_symptoms():
    """Returns the full list of 132 symptoms the model understands."""
    return {"symptoms": feature_columns}

@router.get("/history")
async def get_prediction_history(
    current_user: dict = Depends(get_current_user)
):
    """Returns all past predictions for the logged-in user."""
    result = supabase.table("predictions")\
        .select("*")\
        .eq("user_id", current_user["sub"])\
        .order("created_at", desc=True)\
        .execute()

    return result.data