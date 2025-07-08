# 🔒 SafeWeb
A Real-Time Phishing Detection Browser Extension for Static Web Phishing Detection with Risk-Level Classification

## 📌 Overview

**SafeWeb** is a phishing detection system that combines static webpage analysis with machine learning to identify phishing attempts in real-time. It extracts structural, textual, and visual clues from the webpage's HTML and URL without executing any scripts or requiring screenshots. SafeWeb is delivered via a lightweight **Chrome extension** connected to a **Flask backend API** for real-time classification and risk labeling.

## 🛠️ What We Actually Did

✅ Used the **PhiUSIIL Dataset** (50K phishing, 50K benign)  
✅ Extracted **static features** (URL, HTML structure, text) using Playwright (no-JS)  
✅ Applied **feature selection techniques** (Chi2, Mutual Info, ANOVA, XGBoost)  
✅ Trained an **XGBoost classifier** on selected top features  
✅ Implemented a **risk mapping system** to classify results into Low, Medium, or High  
✅ Created a working **Flask API** for real-time prediction  
✅ Built a **Chrome Extension** that interacts with the API  
✅ Conducted evaluation: AUC, confusion matrix, and ROC analysis  
✅ Identified limitations including slow crawling, no visual/screenshot input, and static keyword dependency

## 📁 Project Structure

SafeWeb/
├── data/                   # Raw & processed datasets (cleaned, selected, final)
├── crawler/                # Playwright crawler for static HTML retrieval
├── features/               # Feature extraction scripts (URL, HTML, text)
├── modeling/               # Model training, feature selection, evaluation
├── backend/                # Flask API server with real-time prediction logic
├── extension/              # Chrome extension to display classification in-browser
├── docs/                   # Research paper, diagrams, screenshots, SHAP
├── tests/                  # Testing scripts (unit, API)
└── README.md               # You are here

## 🧩 Features

- **📦 Dataset**: 100,000 URLs (50k phishing, 50k benign) from PhiUSIIL
- **🧠 Feature Types**:
  - 28 **URL-based** features (e.g., entropy, digit ratio, path depth)
  - 18 **HTML-based** features (e.g., iframe count, external scripts, missing title)
  - 5 **Text-based** features (e.g., TF-IDF terms, text length, sensitive terms)
- **📊 Feature Selection**: Composite-ranked using 4 methods:
  - Chi-Square
  - Mutual Information
  - ANOVA F-test
  - XGBoost Feature Importance
- **🔍 Model**: XGBoost Classifier
- **🧪 Validation**:
  - Stratified 5-Fold Cross-Validation
  - Confusion Matrix & ROC Analysis
  - Sanity Check with Shuffled Labels (AUC ≈ 0.50)
- **📈 Risk Mapping**:
  - **Low Risk**: `0.0 ≤ P(phishing) < 0.3`
  - **Medium Risk**: `0.3 ≤ P(phishing) < 0.7`
  - **High Risk**: `0.7 ≤ P(phishing) ≤ 1.0`

## 🚀 Setup Instructions

### 1. Run Backend API

```bash
cd backend/
pip install -r requirements.txt
python app.py
````

### 2. Load Chrome Extension

* Open `chrome://extensions/`
* Enable **Developer Mode**
* Click **Load Unpacked**
* Select the `extension/` folder

### 3. Run Static HTML Crawler

Use Playwright + Docker to crawl pages for static HTML extraction (non-real-time usage only).

## 📊 Evaluation Metrics (Final Model)

| Metric        | Value (Approx.) |
| ------------- | --------------- |
| Accuracy      | 95.2%           |
| Precision     | 94.7%           |
| Recall        | 94.0%           |
| AUC Score     | 0.967           |
| F1-Score      | 0.945           |
| Cohen’s Kappa | 0.87            |

## 📈 Visual Outputs

* ✅ ROC Curve (True Positive Rate vs. False Positive Rate)
* ✅ Confusion Matrix (TP, FP, TN, FN distribution)
* ✅ SHAP Importance Plot (feature explanations)
* ✅ Sample risk-level classification popup (Low, Medium, High)

## 🧪 Testing

You can test the system by:

* Opening a website
* Observing Chrome Extension popup risk level
* Verifying console debug logs
* Using `/predict` API with raw URL payloads

## ⚠️ System Limitations

* No screenshot or visual similarity analysis
* Static HTML only — no dynamic JS rendering
* Backend runs locally (not deployed in cloud)
* Manual TF-IDF keyword curation
* No multilingual support
* High AUC due to synthetic benign set lacking realistic noise

## 🧠 Future Enhancements

* 🌐 Deploy backend via Render, Railway, or GCP
* 🧩 Add screenshot similarity using CNN
* 🔍 Introduce auto-updating keyword/token lists
* 🌎 Multilingual TF-IDF and LLM-based reasoning

## 📄 References

* PhiUSIIL Dataset
* Playwright (Microsoft)
* XGBoost, Scikit-learn
* SHAP Explainability
* Tranco Top Domains
* Chrome Extensions API

**Authors**: SafeWeb Prototype Research Team
- Suaverdez
- Laxa
- Enriquez

**License**: MIT