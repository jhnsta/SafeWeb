import pandas as pd
import re
import numpy as np
from urllib.parse import urlparse
from collections import Counter
from itertools import groupby
from tqdm import tqdm
import os
import requests
import zipfile
import io
import tldextract
os.makedirs("data/external", exist_ok=True)

tqdm.pandas()

# Load input and keywords
df = pd.read_csv("data/processed/normalized_urls.csv")
with open("data/keywords/suspicious_url_keywords.txt") as f:
    suspicious_tokens = set(line.strip().lower() for line in f if line.strip())

# Load Tranco trusted domains
TRONCO_CACHE = "data/external/tranco_top_10000.txt"

def load_tranco(top_n=10000):
    if os.path.exists(TRONCO_CACHE):
        with open(TRONCO_CACHE, "r") as f:
            return set(f.read().splitlines())

    tranco_url = "https://tranco-list.eu/top-1m.csv.zip"
    r = requests.get(tranco_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, header=None)
        top_sites = df.iloc[:top_n, 1].str.lower().tolist()
        with open(TRONCO_CACHE, "w") as f:
            f.write("\n".join(top_sites))
        return set(top_sites)

TRUSTED = load_tranco(top_n=10000)

def domain_features(normalized_url):
    ext = tldextract.extract(normalized_url)
    root = f"{ext.domain}.{ext.suffix}".lower()
    path = normalized_url.lower()
    is_known = int(root in TRUSTED)
    brand_in_path = int(any(b in path for b in TRUSTED if b in path))
    mismatch = int(brand_in_path and not is_known)
    return is_known, brand_in_path, mismatch

def shannon_entropy(s):
    probabilities = [n_x / len(s) for x, n_x in Counter(s).items()]
    return -sum(p * np.log2(p) for p in probabilities)

def extract_features(url):
    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''

    features = {}
    features['url_length'] = len(url)
    features['entropy'] = shannon_entropy(url)
    features['has_https'] = int(url.startswith("https"))
    features['NoHttps'] = int(not url.startswith("https"))
    features['num_dots'] = url.count('.')
    features['subdomain_level'] = hostname.count('.') - 1 if hostname else 0
    features['path_level'] = path.count('/')
    features['num_dash'] = url.count('-')
    features['at_symbol'] = int('@' in url)
    features['num_underscore'] = url.count('_')
    features['num_numeric_chars'] = sum(c.isdigit() for c in url)
    features['url_shortener_used'] = int(any(service in url for service in ['bit.ly', 'tinyurl', 't.co', 'goo.gl']))
    features['prefix_suffix_in_domain'] = int('-' in hostname)
    features['domain_is_ip'] = int(re.match(r'\d+\.\d+\.\d+\.\d+', hostname or '') is not None)
    features['hostname_length'] = len(hostname)
    features['tld_length'] = len(hostname.split('.')[-1]) if '.' in hostname else 0
    features['HttpsInHostname'] = int('https' in hostname)
    features['DoubleSlashInPath'] = int('//' in path.strip('/'))
    features['RandomString'] = int(bool(re.search(r'[a-zA-Z]{3,}\d{3,}', hostname)))
    features['NumQueryComponents'] = query.count('=') + query.count('&')
    features['QueryLength'] = len(query)
    features['NumAmpersand'] = url.count('&')
    features['NumHash'] = url.count('#')
    features['DomainInSubdomains'] = int(any(kw in hostname.split('.')[:-2] for kw in ['google', 'paypal', 'amazon']))
    features['DomainInPaths'] = int(any(kw in path for kw in ['google', 'paypal', 'amazon']))
    features['CharContinuationRate'] = max([len(list(g)) for _, g in groupby(url)]) / len(url) if url else 0
    features['LetterRatioInURL'] = sum(c.isalpha() for c in url) / len(url)
    features['DigitRatioInURL'] = sum(c.isdigit() for c in url) / len(url)
    features['suspicious_keywords'] = sum(1 for token in re.split(r'\W+', url.lower()) if token in suspicious_tokens)

    # Tranco-based features
    is_known_brand, brand_in_path, brand_domain_mismatch = domain_features(url)
    features['is_known_brand'] = is_known_brand
    features['brand_in_path'] = brand_in_path
    features['brand_domain_mismatch'] = brand_domain_mismatch

    return pd.Series(features)

# Apply with progress bar
print("Extracting URL-based features...")
url_features = df['url'].progress_apply(extract_features)

# Append URL and label
url_features['url'] = df['url']
url_features['label'] = df['label']

# Save
url_features.to_csv("data/features/url_features.csv", index=False)
print("URL-based features saved to data/features/url_features.csv")
