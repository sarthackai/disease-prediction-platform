# pyrefly: ignore [missing-import]
"""
train.py
Trains Random Forest and XGBoost models on the disease-symptom dataset,
compares them, and saves the best one for use by the FastAPI backend.
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from xgboost import XGBClassifier

# ------------------------------------------------------------------
# 1. SETUP PATHS
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_CSV = os.path.join(BASE_DIR, "data", "raw", "Training.csv")
TEST_CSV = os.path.join(BASE_DIR, "data", "raw", "Testing.csv")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "..", "backend", "app", "ml", "artifacts")
REGISTRY_DIR = os.path.join(BASE_DIR, "model_registry")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(REGISTRY_DIR, exist_ok=True)

# ------------------------------------------------------------------
# 2. LOAD DATA
# ------------------------------------------------------------------
print("Loading data...")
train_df = pd.read_csv(TRAIN_CSV)
test_df = pd.read_csv(TEST_CSV)

# Drop any unnamed/empty columns that sometimes appear in this dataset
train_df = train_df.loc[:, ~train_df.columns.str.contains("^Unnamed")]
test_df = test_df.loc[:, ~test_df.columns.str.contains("^Unnamed")]

print(f"Training rows: {len(train_df)}, Testing rows: {len(test_df)}")
print(f"Columns: {len(train_df.columns)}")

# ------------------------------------------------------------------
# 3. SEPARATE FEATURES (symptoms) AND LABEL (disease)
# ------------------------------------------------------------------
LABEL_COL = "prognosis"

X_train = train_df.drop(columns=[LABEL_COL])
y_train_raw = train_df[LABEL_COL]

X_test = test_df.drop(columns=[LABEL_COL])
y_test_raw = test_df[LABEL_COL]

feature_columns = list(X_train.columns)
print(f"Number of symptom features: {len(feature_columns)}")

# Save feature column order — the backend MUST send features in this exact order
with open(os.path.join(ARTIFACTS_DIR, "feature_columns.json"), "w") as f:
    json.dump(feature_columns, f, indent=2)

# ------------------------------------------------------------------
# 4. ENCODE THE DISEASE LABELS (text -> numbers)
# ------------------------------------------------------------------
label_encoder = LabelEncoder()
y_train = label_encoder.fit_transform(y_train_raw)
y_test = label_encoder.transform(y_test_raw)

joblib.dump(label_encoder, os.path.join(ARTIFACTS_DIR, "label_encoder.pkl"))
print(f"Number of disease classes: {len(label_encoder.classes_)}")

# ------------------------------------------------------------------
# 5. TRAIN MODEL 1: RANDOM FOREST
# ------------------------------------------------------------------
print("\nTraining Random Forest...")
rf_model = RandomForestClassifier(n_estimators=200, random_state=42)
rf_model.fit(X_train, y_train)
rf_preds = rf_model.predict(X_test)

rf_metrics = {
    "accuracy": accuracy_score(y_test, rf_preds),
    "precision": precision_score(y_test, rf_preds, average="macro", zero_division=0),
    "recall": recall_score(y_test, rf_preds, average="macro", zero_division=0),
    "f1": f1_score(y_test, rf_preds, average="macro", zero_division=0),
}
print("Random Forest results:", rf_metrics)

# ------------------------------------------------------------------
# 6. TRAIN MODEL 2: XGBOOST
# ------------------------------------------------------------------
print("\nTraining XGBoost...")
xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    random_state=42,
    eval_metric="mlogloss"
)
xgb_model.fit(X_train, y_train)
xgb_preds = xgb_model.predict(X_test)

xgb_metrics = {
    "accuracy": accuracy_score(y_test, xgb_preds),
    "precision": precision_score(y_test, xgb_preds, average="macro", zero_division=0),
    "recall": recall_score(y_test, xgb_preds, average="macro", zero_division=0),
    "f1": f1_score(y_test, xgb_preds, average="macro", zero_division=0),
}
print("XGBoost results:", xgb_metrics)

# ------------------------------------------------------------------
# 7. COMPARE AND PICK THE BEST MODEL (by F1 score)
# ------------------------------------------------------------------
if xgb_metrics["f1"] >= rf_metrics["f1"]:
    best_model = xgb_model
    best_name = "xgboost"
    best_metrics = xgb_metrics
else:
    best_model = rf_model
    best_name = "random_forest"
    best_metrics = rf_metrics

print(f"\nBest model: {best_name}")
print(f"Best metrics: {best_metrics}")

# ------------------------------------------------------------------
# 8. SAVE THE BEST MODEL + VERSION INFO
# ------------------------------------------------------------------
joblib.dump(best_model, os.path.join(ARTIFACTS_DIR, "model.pkl"))

with open(os.path.join(ARTIFACTS_DIR, "version.txt"), "w") as f:
    f.write(f"{best_name}_v1")

# ------------------------------------------------------------------
# 9. WRITE A COMPARISON REPORT (for your project documentation)
# ------------------------------------------------------------------
report_lines = [
    "# Model Comparison Report\n",
    f"Dataset: {len(train_df)} training rows, {len(test_df)} testing rows\n",
    f"Number of disease classes: {len(label_encoder.classes_)}\n",
    f"Number of symptom features: {len(feature_columns)}\n\n",
    "## Random Forest\n",
    f"- Accuracy: {rf_metrics['accuracy']:.4f}\n",
    f"- Precision: {rf_metrics['precision']:.4f}\n",
    f"- Recall: {rf_metrics['recall']:.4f}\n",
    f"- F1 Score: {rf_metrics['f1']:.4f}\n\n",
    "## XGBoost\n",
    f"- Accuracy: {xgb_metrics['accuracy']:.4f}\n",
    f"- Precision: {xgb_metrics['precision']:.4f}\n",
    f"- Recall: {xgb_metrics['recall']:.4f}\n",
    f"- F1 Score: {xgb_metrics['f1']:.4f}\n\n",
    f"## Selected Model: {best_name}\n",
    f"Reason: highest macro F1 score ({best_metrics['f1']:.4f})\n",
]

with open(os.path.join(REGISTRY_DIR, "comparison_report.md"), "w") as f:
    f.writelines(report_lines)

print("\n✅ Done. Model saved to backend/app/ml/artifacts/model.pkl")
print("✅ Comparison report saved to ml-training/model_registry/comparison_report.md")