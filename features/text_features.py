import pandas as pd
import re
from tqdm import tqdm
import requests
import zipfile
import io
import os

# Enable progress bar
tqdm.pandas()

# Load dataset
df = pd.read_csv("data/processed/normalized_urls.csv")

# Load suspicious terms
with open("data/keywords/suspicious_text_terms.txt") as f:
    suspicious_terms = set(line.strip().lower() for line in f if line.strip())

# Load sensitive terms from file only
with open("data/keywords/sensitive_terms.txt") as f:
    sensitive_terms = set(line.strip().lower() for line in f if line.strip())

# Load known brand names with local file fallback only
def load_known_brands():
    try:
        resp = requests.get("https://tranco-list.eu/top-1m.csv.zip", timeout=10)
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            with z.open(z.namelist()[0]) as f:
                df_zip = pd.read_csv(f, header=None)
                domains = df_zip[1].dropna().str.split('.').str[0].unique()[:500]
                return set(domains)
    except:
        with open("data/keywords/known_brands.txt") as f:
            return set(line.strip().lower() for line in f if line.strip())

known_brands = load_known_brands()

# Feature extraction
def extract_text_features(text):
    text = str(text).lower()
    words = re.findall(r'\b\w+\b', text)

    return pd.Series({
        "text_length": len(text),
        "suspicious_text_terms": sum(1 for w in words if w in suspicious_terms),
        "num_text_words": len(words),
        "NumSensitiveWords": sum(1 for t in sensitive_terms if t in text),
        "EmbeddedBrandName": int(any(brand in text for brand in known_brands)),
    })

# Apply with progress bar
print("Extracting text-based features...")
text_features = df['visible_text'].fillna('').progress_apply(extract_text_features)

# Add metadata
text_features['url'] = df['url']
text_features['label'] = df['label']

# Save to file
output_path = "data/features/text_features.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
text_features.to_csv(output_path, index=False)
print(f"Text-based features saved to {output_path}")
