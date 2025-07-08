import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm
import joblib

# Enable progress bars
tqdm.pandas()

# Load the cleaned combined dataset (with raw_html and visible_text still present)
df = pd.read_csv("data/processed/normalized_urls.csv")

# Extract visible text
text_series = df['visible_text'].fillna('').astype(str)

# Wrap vectorizer transform in tqdm for progress visibility
print("Transforming TF-IDF features...")
vectorizer = TfidfVectorizer(stop_words='english', max_features=300)
tfidf_matrix = vectorizer.fit_transform(tqdm(text_series, desc="TF-IDF Progress"))

# Convert to DataFrame and binarize (presence = 1, absence = 0)
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=[f"tfidf_{t}" for t in vectorizer.get_feature_names_out()])
tfidf_df = (tfidf_df > 0).astype(int)

# Add metadata for later merge
tfidf_df['url'] = df['url']
tfidf_df['label'] = df['label']

# Save TF-IDF feature set
tfidf_df.to_csv("data/features/tfidf_features.csv", index=False)
print("TF-IDF features saved to data/features/tfidf_features.csv")

# Save fitted vectorizer
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
print("TF-IDF vectorizer saved to models/tfidf_vectorizer.pkl")
