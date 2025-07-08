import pandas as pd

# Assume you have a split
train_df = pd.read_csv("data/processed/training_dataset.csv")
val_df = pd.read_csv("data/processed/validation_dataset.csv")

X_train = train_df.drop(columns=["label"])
y_train = train_df["label"]
X_val = val_df.drop(columns=["label"])
y_val = val_df["label"]

model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

y_pred = model.predict(X_val)
y_proba = model.predict_proba(X_val)[:, 1]

print("Validation AUC:", roc_auc_score(y_val, y_proba))