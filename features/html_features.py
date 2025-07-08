import pandas as pd
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

tqdm.pandas()

# Load combined raw HTML data
df = pd.read_csv("data/processed/normalized_urls.csv")

def extract_html_features(html):
    soup = BeautifulSoup(html, "html.parser")
    features = {}

    # Basic tag counts
    features['iframe_count'] = len(soup.find_all("iframe"))
    features['eval_present'] = int("eval(" in html)
    features['form_action_external'] = 0
    features['base64_scripts'] = len(re.findall(r"(eval\(|base64,)", html))
    features['has_favicon'] = int(bool(soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")))
    features['has_title'] = int(bool(soup.title and soup.title.string))
    features['MissingTitle'] = int(not (soup.title and soup.title.string))

    features['num_external_links'] = sum(1 for a in soup.find_all('a', href=True) if re.match(r'https?://', a['href']))
    features['num_img_tags'] = len(soup.find_all("img"))
    features['num_script_tags'] = len(soup.find_all("script"))
    features['num_meta_tags'] = len(soup.find_all("meta"))

    images_only_forms = 0
    relative_action, external_action, abnormal_action = 0, 0, 0
    null_self_redirects = 0

    forms = soup.find_all("form")
    for form in forms:
        inputs = form.find_all("input")
        has_only_images = all(inp.get("type") == "image" for inp in inputs if inp.get("type"))
        if has_only_images and inputs:
            images_only_forms += 1

        action = form.get("action", "").strip()
        if action.startswith("/"):
            relative_action += 1
        elif re.match(r'https?://', action):
            external_action += 1
        elif not action or "?" in action or "javascript" in action.lower():
            abnormal_action += 1

    features["ImagesOnlyInForm"] = images_only_forms
    features["PctExtHyperlinks"] = features['num_external_links'] / max(len(soup.find_all("a")), 1)
    features["PctExtResourceUrls"] = (
        sum(1 for tag in soup.find_all(["script", "img", "link"]) if tag.get("src") and re.match(r'https?://', tag.get("src", "")))
        / max(len(soup.find_all(["script", "img", "link"])), 1)
    )
    features["RelativeFormAction"] = relative_action
    features["ExtFormAction"] = external_action
    features["AbnormalFormAction"] = abnormal_action

    null_self_redirects = sum(
        1 for a in soup.find_all('a', href=True)
        if a['href'].strip() in ['#', '/', '', 'javascript:void(0)', 'javascript:;']
    )
    features["PctExtNullSelfRedirectHyperlinks"] = null_self_redirects / max(len(soup.find_all("a")), 1)

    return pd.Series(features)

# Extract with progress bar
print("Extracting HTML-based features...")
html_features = df['raw_html'].fillna('').progress_apply(extract_html_features)

# Add metadata
html_features['url'] = df['url']
html_features['label'] = df['label']

# Save
html_features.to_csv("data/features/html_features.csv", index=False)
print("HTML-based features saved to data/features/html_features.csv")
