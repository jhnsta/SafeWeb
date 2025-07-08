import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from pathlib import Path

# Load and filter phishing samples
df = pd.read_csv("data/processed/normalized_urls.csv")
phish_df = df[df["label"] == 0]

# --- Suspicious URL Keyword Extraction ---
def extract_url_tokens(url):
    return re.findall(r'\b\w+\b', url.lower())

url_tokens = phish_df['url'].apply(extract_url_tokens).explode()
url_freq = url_tokens.value_counts().head(100)

Path("data/keywords").mkdir(parents=True, exist_ok=True)
with open("data/keywords/suspicious_url_keywords.txt", "w") as f:
    for token in url_freq.index:
        f.write(f"{token}\n")

# --- Suspicious Text Term Extraction ---
vectorizer = CountVectorizer(stop_words="english", max_features=100)
text_data = phish_df['visible_text'].fillna('')
X = vectorizer.fit_transform(text_data)
top_text_terms = vectorizer.get_feature_names_out()

with open("data/keywords/suspicious_text_terms.txt", "w") as f:
    for term in top_text_terms:
        f.write(f"{term}\n")

print("Suspicious keyword files generated.")
