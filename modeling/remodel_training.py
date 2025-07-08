import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score
from sklearn.utils import shuffle
from sklearn.metrics import roc_auc_score
import numpy as np

# Load your dataset
df = pd.read_csv("data/processed/training_dataset.csv")
X = df.drop(columns=["label"])
y = df["label"]

# Shuffle the labels (to break true relationship)
y_shuffled = shuffle(y, random_state=42)

# Train model on shuffled labels
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
scores = cross_val_score(model, X, y_shuffled, cv=5, scoring='roc_auc')

print("Sanity Check (Shuffled Labels):")
print("Mean AUC:", np.mean(scores))
