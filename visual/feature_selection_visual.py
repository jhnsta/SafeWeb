import pandas as pd
import matplotlib.pyplot as plt
import os

# Load feature importance scores
df = pd.read_csv("data/processed/feature_selection_scores.csv")

# Ensure output directory exists
os.makedirs("visual", exist_ok=True)

# Function to create and save bar chart for a given metric
def plot_top_features(metric, top_n=30):
    sorted_df = df.sort_values(by=metric, ascending=False).head(top_n)
    plt.figure(figsize=(10, 8))
    plt.barh(sorted_df['feature'], sorted_df[metric], color='skyblue')
    plt.xlabel(f'{metric} Score')
    plt.title(f'Top {top_n} Features by {metric}')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f"visual/top_{top_n}_features_{metric}.png")
    plt.close()

# Generate plots for each metric
for metric in ['chi2', 'anova_f', 'mutual_info', 'xgboost_importance']:
    plot_top_features(metric)

print("Visualizations saved to the 'visual' folder.")
