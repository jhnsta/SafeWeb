import pandas as pd
import numpy as np
import os
os.makedirs("models", exist_ok=True)
os.makedirs("visual", exist_ok=True)
from urllib.parse import urlparse, urlunparse

from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    cohen_kappa_score, roc_auc_score, confusion_matrix
)
from sklearn.metrics import RocCurveDisplay
from xgboost import XGBClassifier
import joblib
import matplotlib.pyplot as plt

# 1. Load training data
df = pd.read_csv("data/processed/training_dataset.csv")
X = df.drop(columns=['label'])
y = df['label']
print("Dataset loaded:", X.shape, "features + label.")

# 3. Stratified 5-Fold CV
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
accs, precs, recs, kappas, aucs = [], [], [], [], []

print("\nRunning Stratified 5‑Fold CV…")
for fold, (train_idx, test_idx) in enumerate(kf.split(X, y), start=1):
    X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
    y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_tr, y_tr)

    preds = model.predict(X_te)
    probs = model.predict_proba(X_te)[:, 1]

    accs.append(accuracy_score(y_te, preds))
    precs.append(precision_score(y_te, preds))
    recs.append(recall_score(y_te, preds))
    kappas.append(cohen_kappa_score(y_te, preds))
    aucs.append(roc_auc_score(y_te, probs))
    print(f" Fold {fold} — AUC: {aucs[-1]:.4f}")

print("\nCross‑Val Results (mean ± std):")
print(f" Accuracy      : {np.mean(accs):.4f} ± {np.std(accs):.4f}")
print(f" Precision     : {np.mean(precs):.4f} ± {np.std(precs):.4f}")
print(f" Recall        : {np.mean(recs):.4f} ± {np.std(recs):.4f}")
print(f" Cohen's Kappa : {np.mean(kappas):.4f} ± {np.std(kappas):.4f}")
print(f" ROC AUC       : {np.mean(aucs):.4f} ± {np.std(aucs):.4f}")

# 4. Hyperparameter tuning
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [3, 6],
    'learning_rate': [0.05, 0.1],
    'subsample': [0.8, 1]
}
grid = GridSearchCV(
    XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
    param_grid, cv=3, scoring='roc_auc', n_jobs=-1
)
grid.fit(X, y)
print("\nBest parameters found:", grid.best_params_)

# 5. Final model training
final_model = grid.best_estimator_
final_model.fit(X, y)

# 6. Probability → Risk mapping function
def map_risk(prob_benign):
    prob_phish = 1 - prob_benign
    return "High" if prob_phish > 0.7 else "Medium" if prob_phish > 0.3 else "Low"

# Use benign probabilities from model
probs = final_model.predict_proba(X)[:, 1]  # P(benign)
risk_levels = [map_risk(p) for p in probs]

# 7. Save final model
joblib.dump(final_model, "models/xgb_modelv3.pkl")
print("\nFinal XGBoost model saved to models/xgb_modelv3.pkl")

# 8. Save ROC curve (using the last fold)
RocCurveDisplay.from_estimator(model, X_te, y_te)
plt.title("ROC Curve (Last Fold)")
plt.savefig("visual/roc_last_fold.png")
plt.close()

# 9. Save confusion matrix
cm = confusion_matrix(y_te, preds)
plt.figure(figsize=(4,4))
plt.matshow(cm, cmap='Blues', fignum=1)
plt.title("Confusion Matrix (Last Fold)")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("True")
plt.xticks([0,1])
plt.yticks([0,1])
plt.savefig("visual/confusion_matrix_last_fold.png")
plt.close()

print("\nROC & confusion matrix images saved in visual/")
