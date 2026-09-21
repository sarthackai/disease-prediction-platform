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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
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
# 6b. CROSS-VALIDATION (more reliable performance estimate)
# ------------------------------------------------------------------
print("\nRunning 5-Fold Cross Validation...")
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

rf_cv_scores = cross_val_score(
    RandomForestClassifier(n_estimators=200, random_state=42),
    X_train, y_train,
    cv=kfold,
    scoring="f1_macro"
)
print(f"Random Forest CV F1: {rf_cv_scores.mean():.4f} +/- {rf_cv_scores.std():.4f}")

xgb_cv_scores = cross_val_score(
    XGBClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        eval_metric="mlogloss"
    ),
    X_train, y_train,
    cv=kfold,
    scoring="f1_macro"
)
print(f"XGBoost CV F1:       {xgb_cv_scores.mean():.4f} +/- {xgb_cv_scores.std():.4f}")

# Save CV results to report
cv_results = {
    "random_forest": {
        "cv_f1_mean": round(float(rf_cv_scores.mean()), 4),
        "cv_f1_std":  round(float(rf_cv_scores.std()),  4),
        "cv_scores":  [round(float(s), 4) for s in rf_cv_scores]
    },
    "xgboost": {
        "cv_f1_mean": round(float(xgb_cv_scores.mean()), 4),
        "cv_f1_std":  round(float(xgb_cv_scores.std()),  4),
        "cv_scores":  [round(float(s), 4) for s in xgb_cv_scores]
    }
}

import json
with open(os.path.join(REGISTRY_DIR, "cv_results.json"), "w") as f:
    json.dump(cv_results, f, indent=2)

print("Cross-validation results saved to model_registry/cv_results.json")



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
# 8. CALIBRATE + SAVE THE BEST MODEL + VERSION INFO
# ------------------------------------------------------------------
print("\nCalibrating model probabilities...")

# Save uncalibrated model first as backup
joblib.dump(best_model, os.path.join(ARTIFACTS_DIR, "model_uncalibrated.pkl"))

# Calibrate using cross-validation on training data
calibrated_model = CalibratedClassifierCV(
    estimator=RandomForestClassifier(n_estimators=200, random_state=42)
    if best_name == "random_forest"
    else XGBClassifier(n_estimators=200, max_depth=6, random_state=42, eval_metric="mlogloss"),
    method="sigmoid",
    cv=5
)
calibrated_model.fit(X_train, y_train)

# Verify calibrated model still performs well
cal_preds = calibrated_model.predict(X_test)
cal_f1 = f1_score(y_test, cal_preds, average="macro", zero_division=0)
print(f"Calibrated model F1: {cal_f1:.4f}")

# Save calibrated model
joblib.dump(calibrated_model, os.path.join(ARTIFACTS_DIR, "model.pkl"))
print("Calibrated model saved.")

# ------------------------------------------------------------------
# 8b. CONFUSION MATRIX + PER-DISEASE METRICS
# ------------------------------------------------------------------
print("\nGenerating confusion matrix and per-disease metrics...")

best_preds = calibrated_model.predict(X_test)
disease_names = list(label_encoder.classes_)

# Confusion matrix
cm = confusion_matrix(y_test, best_preds)

# Find confused disease pairs
confused_pairs = []
for i in range(len(cm)):
    for j in range(len(cm)):
        if i != j and cm[i][j] > 0:
            confused_pairs.append({
                "actual":    disease_names[i],
                "predicted": disease_names[j],
                "count":     int(cm[i][j])
            })
confused_pairs.sort(key=lambda x: x["count"], reverse=True)

with open(os.path.join(REGISTRY_DIR, "confusion_analysis.json"), "w") as f:
    json.dump(confused_pairs[:10], f, indent=2)

print("Top confused disease pairs:")
for pair in confused_pairs[:5]:
    print(f"  {pair['actual']} → {pair['predicted']}: {pair['count']} time(s)")

# Per-disease metrics
report_dict = classification_report(
    y_test,
    best_preds,
    target_names=disease_names,
    output_dict=True,
    zero_division=0
)

per_disease_metrics = []
for disease in disease_names:
    if disease in report_dict:
        per_disease_metrics.append({
            "disease":   disease,
            "precision": round(report_dict[disease]["precision"], 4),
            "recall":    round(report_dict[disease]["recall"],    4),
            "f1":        round(report_dict[disease]["f1-score"],  4),
            "support":   int(report_dict[disease]["support"])
        })

per_disease_metrics.sort(key=lambda x: x["f1"])

with open(os.path.join(REGISTRY_DIR, "per_disease_metrics.json"), "w") as f:
    json.dump(per_disease_metrics, f, indent=2)

print("\nLowest performing diseases:")
for d in per_disease_metrics[:5]:
    print(f"  {d['disease']}: F1={d['f1']}")

print("\nHighest performing diseases:")
for d in per_disease_metrics[-5:]:
    print(f"  {d['disease']}: F1={d['f1']}")

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

# Also save a model card JSON
model_card = {
    "model_version":   f"{best_name}_v1",
    "model_type":      best_name,
    "calibrated":      True,
    "dataset": {
        "training_rows": len(X_train),
        "testing_rows":  len(X_test),
        "n_features":    len(feature_columns),
        "n_classes":     len(label_encoder.classes_)
    },
    "test_metrics":    best_metrics,
    "cv_metrics": {
        "random_forest_f1_mean": round(float(rf_cv_scores.mean()), 4),
        "xgboost_f1_mean":       round(float(xgb_cv_scores.mean()), 4)
    },
    "diseases": list(label_encoder.classes_)
}

with open(os.path.join(ARTIFACTS_DIR, "model_card.json"), "w") as f:
    json.dump(model_card, f, indent=2)

print("Model card saved to backend/app/ml/artifacts/model_card.json")

# ------------------------------------------------------------------
# 10. SYMPTOM SEVERITY WEIGHTING (using SHAP importance)
# ------------------------------------------------------------------
print("\nCalculating symptom severity weights using SHAP...")
import shap

shap_explainer = shap.TreeExplainer(best_model)

# Use a sample of training data for speed
sample_size = min(100, len(X_train))
X_sample = X_train[:sample_size]
shap_values = shap_explainer.shap_values(X_sample)

# Average absolute SHAP value per symptom across all classes
sv = np.array(shap_values)
print(f"SHAP values shape: {sv.shape}")

if sv.ndim == 3:
    # Shape (n_classes, n_samples, n_features) — Random Forest
    mean_shap = np.mean(np.abs(sv), axis=(0, 1))
elif sv.ndim == 2:
    # Shape (n_samples, n_features) — XGBoost
    mean_shap = np.mean(np.abs(sv), axis=0)
else:
    mean_shap = np.abs(sv).flatten()

# Safety check — if shape doesn't match features, use feature importances
print(f"mean_shap length: {len(mean_shap)}, feature_columns length: {len(feature_columns)}")
if len(mean_shap) != len(feature_columns):
    print("Shape mismatch — using feature importances as fallback")
    # Get base model from calibrated wrapper
    if hasattr(calibrated_model, "estimators_"):
        base_importances = np.mean(
            [est.feature_importances_ for est in calibrated_model.estimators_],
            axis=0
        )
    elif hasattr(calibrated_model, "base_estimator"):
        base_importances = calibrated_model.base_estimator.feature_importances_
    else:
        # Direct fallback — use best_model feature importances
        base_importances = best_model.feature_importances_
    mean_shap = base_importances

# Build symptom weights dictionary
symptom_weights = {
    feature_columns[i]: round(float(mean_shap[i]), 6)
    for i in range(len(feature_columns))
}

# Sort by importance
symptom_weights_sorted = dict(
    sorted(symptom_weights.items(), key=lambda x: x[1], reverse=True)
)

with open(os.path.join(ARTIFACTS_DIR, "symptom_weights.json"), "w") as f:
    json.dump(symptom_weights_sorted, f, indent=2)

print("\nTop 10 most diagnostically important symptoms:")
for symptom, weight in list(symptom_weights_sorted.items())[:10]:
    print(f"  {symptom}: {weight}")

# ------------------------------------------------------------------
# 11. SYMPTOM CO-OCCURRENCE ANALYSIS
# ------------------------------------------------------------------
print("\nAnalyzing symptom co-occurrences...")

cooccurrence = X_train.T.dot(X_train)
cols = list(X_train.columns)

pairs = []
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        count = int(cooccurrence.iloc[i, j])
        if count > 0:
            pairs.append({
                "symptom_1":      cols[i],
                "symptom_2":      cols[j],
                "co_occurrences": count
            })

pairs.sort(key=lambda x: x["co_occurrences"], reverse=True)

with open(os.path.join(REGISTRY_DIR, "symptom_cooccurrence.json"), "w") as f:
    json.dump(pairs[:50], f, indent=2)

print("Top 5 co-occurring symptom pairs:")
for p in pairs[:5]:
    print(f"  {p['symptom_1']} + {p['symptom_2']}: {p['co_occurrences']} times")

print("\n✅ Done. Model saved to backend/app/ml/artifacts/model.pkl")
print("✅ Comparison report saved to ml-training/model_registry/comparison_report.md")