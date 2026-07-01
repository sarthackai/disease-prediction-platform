"""
inference.py
Loads the saved model and runs predictions.
Called once at startup — model stays in memory for fast responses.
"""
import joblib
import json
import os
import numpy as np
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

# Load model artifacts once at module import time
model = joblib.load(os.path.join(ARTIFACTS_DIR, "model.pkl"))
label_encoder = joblib.load(os.path.join(ARTIFACTS_DIR, "label_encoder.pkl"))

with open(os.path.join(ARTIFACTS_DIR, "feature_columns.json")) as f:
    feature_columns = json.load(f)

with open(os.path.join(ARTIFACTS_DIR, "version.txt")) as f:
    model_version = f.read().strip()

def encode_symptoms(symptoms: List[str]) -> np.ndarray:
    """
    Converts a list of symptom names into a binary feature vector
    matching the exact 132-column order the model was trained on.
    """
    vector = {col: 0 for col in feature_columns}
    for symptom in symptoms:
        cleaned = symptom.strip().lower().replace(" ", "_")
        if cleaned in vector:
            vector[cleaned] = 1
    return np.array([list(vector.values())])

def predict_disease(symptoms: List[str]) -> Dict[str, Any]:
    """
    Runs the model on the given symptoms and returns:
    - predicted disease name
    - confidence score
    - top 5 predictions with probabilities
    - model version used
    """
    input_vector = encode_symptoms(symptoms)

    # Get probabilities for all 41 disease classes
    probabilities = model.predict_proba(input_vector)[0]

    # Top 5 predictions
    top5_indices = np.argsort(probabilities)[::-1][:5]
    top_predictions = [
        {
            "disease": label_encoder.classes_[i],
            "probability": round(float(probabilities[i]), 4)
        }
        for i in top5_indices
    ]

    # Best prediction
    best_index = top5_indices[0]
    predicted_disease = label_encoder.classes_[best_index]
    confidence_score = round(float(probabilities[best_index]), 4)

    return {
        "predicted_disease": predicted_disease,
        "confidence_score": confidence_score,
        "top_predictions": top_predictions,
        "input_vector": input_vector,
        "model_version": model_version,
        "model_used": model_version,
        "symptoms_input": {
            col: int(input_vector[0][i])
            for i, col in enumerate(feature_columns)
        }
    }