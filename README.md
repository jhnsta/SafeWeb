# 🔐🧠 SafeWeb – A Contextual Safety and Credibility Checker for Web Content

SafeWeb is a privacy-aware browser extension that protects users from both phishing threats and online misinformation by combining behavioral anomaly detection with real-time NLP-powered content analysis.

## 🚀 Features


🚨 Behavior Monitor - Flags phishing patterns, domain spoofing,and coercive click behavior

⚠️ Page Risk Score - Combines behavior + content to produce a trust score

📰 Misinformation Detector - Highlights false or misleading claims using NLP and fact-checking APIs

✅ Verify Text - Lets users highlight text and verify its credibility manually

🔗 Verify Link - Checks embedded or selected URLs for risk and trustworthiness

🔍 Trusted Source Suggestion - Offers links to credible sources when possible

## 🧠 Powered By

- **spaCy** – Named Entity Recognition (NER), preprocessing
- **Transformers (BERT, RoBERTa, T5)** – for classification and stance detection
- **Isolation Forest / One-Class SVM** – for user behavior anomaly detection
- **Google Fact Check API**, **VirusTotal**, **Media Bias Fact Check**

## 🛠️ Technologies Used

- **JavaScript** – browser extension UI and content scripts
- **Python (Flask)** – backend API for ML/NLP models
- **HTML/CSS** – popup and UI components
- **VS Code**, **Git**, **GitHub Projects** – dev environment and planning

## 🧪 Development Setup

```bash
# Clone the repo
git clone https://github.com/jhnsta/SafeWeb.git
cd safeweb-extension

# For backend (Python)
cd backend-api
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r ../requirements.txt

# You can load the browser-extension/ folder as an unpacked extension in Chrome/Firefox for testing.
```

## 📂 Repo Structure
safeweb-extension/

├── browser-extension/      # JS extension logic

├── backend-api/            # Flask backend + NLP/ML

├── models/                 # ML model checkpoints

├── data/                   # Sample datasets

├── docs/                   # Research & planning files

├── tests/                  # Backend and extension tests

## 📌 Status
SafeWeb is currently under active development as a research prototype. Some features may be stubbed or in-progress.

## 👥 Authors
Jhona, Raphael, Jamie

## 📄 License
This project is open source and available under the MIT License.

### ✅ To Use This:

1. In your `safeweb-extension/` folder, open `README.md` in VS Code or Git Bash:
   ```bash
   nano README.md
   ```