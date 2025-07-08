import pandas as pd

# Loads
full_df = pd.read_csv("data/processed/cleaned_dataset.csv")
selected = pd.read_csv("data/processed/final_selected_features.csv")
selected_features = selected['feature'].tolist()

# Remove those you don't want
for f in ['suspicious_keywords', 'NumSensitiveWords', 'suspicious_text_terms']:
    selected_features = [feat for feat in selected_features if feat != f]

# Add important manual features if present
for feat in ['brand_domain_mismatch','iframe_count']:
    if feat not in selected_features and feat in full_df.columns:
        selected_features.append(feat)

# Build the final dataframe
final_df = full_df[selected_features + ['label']]

# Save
final_df.to_csv("data/processed/training_dataset.csv", index=False)
print("Saved with features:", selected_features)
