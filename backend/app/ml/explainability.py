"""
explainability.py
Generates SHAP explanations for predictions.
Handles both Random Forest and XGBoost output shapes correctly.
"""
import shap
import numpy as np
import joblib
import os
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

model = joblib.load(os.path.join(ARTIFACTS_DIR, "model.pkl"))
explainer = shap.TreeExplainer(model)

def get_shap_explanation(
    input_vector: np.ndarray,
    feature_columns: List[str],
    predicted_class_index: int,
    top_n: int = 5
) -> List[Dict]:
    """
    Returns top N symptoms that most influenced the prediction.
    Handles all possible SHAP output shapes safely.
    """
    try:
        shap_values = explainer.shap_values(input_vector)
        sv = np.array(shap_values)

        # Debug shape
        print(f"SHAP values shape: {sv.shape}")
        print(f"predicted_class_index: {predicted_class_index}")
        print(f"feature_columns count: {len(feature_columns)}")

        # Handle different shapes:
        # Shape (n_classes, n_samples, n_features) — Random Forest
        if sv.ndim == 3:
            class_shap = sv[predicted_class_index, 0, :]
        # Shape (n_samples, n_features) — XGBoost binary or single output
        elif sv.ndim == 2:
            class_shap = sv[0, :]
        # Shape (n_features,) — already flat
        elif sv.ndim == 1:
            class_shap = sv
        else:
            # Fallback: use feature importances instead
            class_shap = model.feature_importances_

        # Ensure length matches feature columns
        if len(class_shap) != len(feature_columns):
            print(f"Shape mismatch — using feature importances as fallback")
            class_shap = model.feature_importances_

        # Build symptom-shap pairs
        symptom_shap_pairs = [
            {
                "symptom": feature_columns[i],
                "shap_value": round(float(class_shap[i]), 4)
            }
            for i in range(len(feature_columns))
        ]

        # Return top N by absolute value
        top_symptoms = sorted(
            symptom_shap_pairs,
            key=lambda x: abs(x["shap_value"]),
            reverse=True
        )[:top_n]

        return top_symptoms

    except Exception as e:
        print(f"SHAP explanation failed: {e} — using feature importances")
        # Safe fallback: use model's built-in feature importances
        importances = model.feature_importances_
        pairs = [
            {
                "symptom": feature_columns[i],
                "shap_value": round(float(importances[i]), 4)
            }
            for i in range(len(feature_columns))
        ]
        return sorted(pairs, key=lambda x: abs(x["shap_value"]), reverse=True)[:top_n]