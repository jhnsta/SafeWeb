from flask import Flask, request, jsonify
import joblib
import pandas as pd
import re
import numpy as np
from urllib.parse import urlparse
from collections import Counter
from itertools import groupby
from bs4 import BeautifulSoup
import requests
import tldextract

app = Flask(__name__)

# Load model & vectorizer
model = joblib.load("models/xgb_model.pkl")
tfidf_vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

# Load known/trusted domains
with open("data/external/tranco_top_10000.txt") as f:
    trusted_domains = set(f.read().splitlines())

# Final selected features
SELECTED_FEATURES = [
    'text_length', 'num_img_tags', 'has_https', 'path_level', 'DigitRatioInURL',
    'is_known_brand', 'CharContinuationRate', 'num_numeric_chars', 'tfidf_domain',
    'num_text_words', 'tfidf_seeing', 'tfidf_news', 'tfidf_home',
    'PctExtNullSelfRedirectHyperlinks', 'tfidf_make', 'LetterRatioInURL',
    'tfidf_terms', 'url_length', 'num_meta_tags', 'num_script_tags',
    'has_favicon', 'tfidf_search', 'PctExtHyperlinks', 'hostname_length',
    'tfidf_new', 'tfidf_years', 'num_external_links', 'tfidf_privacy',
    'tfidf_media', 'PctExtResourceUrls', 'tfidf_events', 'tfidf_world', 'entropy',
    'prefix_suffix_in_domain', 'tfidf_time', 'tfidf_2025', 'brand_in_path',
    'tfidf_10', 'tfidf_2024', 'tfidf_25', 'tfidf_best', 'tfidf_contact',
    'tfidf_deployed', 'tfidf_facebook', 'tfidf_finished', 'tfidf_hosting',
    'NoHttps', 'num_dash', 'tfidf_latest', 'tfidf_policy', 'tfidf_read',
    'tfidf_reasons', 'tfidf_refer', 'tfidf_rights', 'tfidf_skip', 'tfidf_view',
    'tfidf_20', 'tfidf_12', 'brand_domain_mismatch', 'iframe_count'
]

def shannon_entropy(s):
    probs = [cnt / len(s) for cnt in Counter(s).values()]
    return -sum(p * np.log2(p) for p in probs) if s else 0

def domain_features(url):
    ext = tldextract.extract(url)
    root = f"{ext.domain}.{ext.suffix}".lower()
    path = url.lower()
    is_known = int(root in trusted_domains)
    brand_in_path = int(any(b in path for b in trusted_domains if b in path))
    mismatch = int(brand_in_path and not is_known)
    return is_known, brand_in_path, mismatch

def extract_url_features(url):
    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''
    f = {}
    f['url_length'] = len(url)
    f['entropy'] = shannon_entropy(url)
    f['has_https'] = int(url.startswith("https"))
    f['NoHttps'] = int(not url.startswith("https"))
    f['num_numeric_chars'] = sum(c.isdigit() for c in url)
    f['num_dash'] = url.count('-')
    f['path_level'] = path.count('/')
    f['CharContinuationRate'] = max(len(list(g)) for _, g in groupby(url)) / len(url) if url else 0
    f['LetterRatioInURL'] = sum(c.isalpha() for c in url) / len(url)
    f['DigitRatioInURL'] = sum(c.isdigit() for c in url) / len(url)
    f['hostname_length'] = len(hostname)
    f['prefix_suffix_in_domain'] = int('-' in hostname)

    is_known_brand, brand_in_path, brand_domain_mismatch = domain_features(url)
    f['is_known_brand'] = is_known_brand
    f['brand_in_path'] = brand_in_path
    f['brand_domain_mismatch'] = brand_domain_mismatch
    return f

def extract_html_features(html):
    soup = BeautifulSoup(html, 'html.parser')
    f = {}
    f['iframe_count'] = len(soup.find_all("iframe"))
    f['has_favicon'] = int(bool(soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")))
    f['num_img_tags'] = len(soup.find_all("img"))
    f['num_script_tags'] = len(soup.find_all("script"))
    f['num_meta_tags'] = len(soup.find_all("meta"))
    anchors = soup.find_all('a', href=True)
    all_tags = soup.find_all(["img", "script", "link"])
    f['num_external_links'] = sum(1 for a in anchors if a['href'].strip().startswith(('http://', 'https://')))
    f['PctExtHyperlinks'] = f['num_external_links'] / max(1, len(anchors))
    f['PctExtResourceUrls'] = sum(1 for tag in all_tags if tag.get("src", "").startswith(('http://', 'https://'))) / max(1, len(all_tags))
    f['PctExtNullSelfRedirectHyperlinks'] = sum(
        1 for a in anchors if a.get("href", "").strip() in ['#', '/', '', 'javascript:void(0)', 'javascript:;']
    ) / max(1, len(anchors))
    return f

def extract_text_features(text):
    text = text or ""
    words = re.findall(r'\b\w+\b', text.lower())
    return {
        'text_length': len(text),
        'num_text_words': len(words)
    }

def extract_tfidf_features(text):
    vec = tfidf_vectorizer.transform([text or ""])
    tfidf_vals = vec.toarray()[0]
    return {f"tfidf_{feat}": val for feat, val in zip(tfidf_vectorizer.get_feature_names_out(), tfidf_vals)}

def extract_all_features(url):
    try:
        resp = requests.get(url, timeout=10)
        html = resp.text
    except:
        html = ""

    text = BeautifulSoup(html, 'html.parser').get_text(separator=" ")

    print("\n🟡 [DEBUG] URL:", url)
    print("🟡 [DEBUG] HTML length:", len(html))
    print("🟡 [DEBUG] Visible text length:", len(text))

    features = {}
    url_feats = extract_url_features(url)
    html_feats = extract_html_features(html)
    text_feats = extract_text_features(text)
    tfidf_feats = extract_tfidf_features(text)

    print("🟢 [DEBUG] URL features:", url_feats)
    print("🟢 [DEBUG] HTML features:", html_feats)
    print("🟢 [DEBUG] Text features:", text_feats)
    print("🟢 [DEBUG] TF-IDF (non-zero):", {k: v for k, v in tfidf_feats.items() if v > 0})

    features.update(url_feats)
    features.update(html_feats)
    features.update(text_feats)
    features.update(tfidf_feats)

    return {k: features.get(k, 0) for k in SELECTED_FEATURES}

def normalize_url(url):
    url = str(url).strip()
    return url.rstrip('/')

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    url = normalize_url(data.get("url"))
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    feats = extract_all_features(url)
    X = pd.DataFrame([feats])[SELECTED_FEATURES]
    prob_benign = model.predict_proba(X)[0, 1]
    prob_phish = 1 - prob_benign
    risk = "High" if prob_phish > 0.7 else "Medium" if prob_phish > 0.3 else "Low"
    return jsonify({
        "url": url,
        "probability_phishing": round(float(prob_phish), 4),
        "risk": risk
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)