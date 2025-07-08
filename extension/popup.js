document.addEventListener("DOMContentLoaded", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: "getPageData" }, (response) => {
      fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: response.url })
      })
        .then(res => res.json())
        .then(data => {
          const risk = data.risk.toLowerCase();
          document.getElementById("result").innerHTML = `
            <p><strong>URL:</strong> ${data.url}</p>
            <p><strong>Phishing Probability:</strong> ${data.probability_phishing}</p>
            <p><strong>Risk Level:</strong> <span class="risk ${risk}">${data.risk}</span></p>
          `;
        })
        .catch(() => {
          document.getElementById("result").textContent = "Prediction failed.";
        });
    });
  });

  chrome.storage.local.get("scannedLink", (result) => {
    const urlToScan = result.scannedLink;

    if (urlToScan) {
      fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlToScan })
      })
        .then(res => res.json())
        .then(data => {
          chrome.storage.local.remove("scannedLink");
          const risk = data.risk.toLowerCase();
          document.getElementById("result").innerHTML = `
            <p><strong>URL:</strong> ${data.url}</p>
            <p><strong>Phishing Probability:</strong> ${data.probability_phishing}</p>
            <p><strong>Risk Level:</strong> <span class="risk ${risk}">${data.risk}</span></p>
          `;
        })
        .catch(() => {
          document.getElementById("result").textContent = "Prediction failed.";
        });
    }
  });

  document.getElementById("manualScanBtn").addEventListener("click", () => {
    const inputUrl = document.getElementById("manualUrl").value.trim();
    if (!inputUrl) return;

    document.getElementById("result").textContent = "Scanning...";

    fetch("http://localhost:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: inputUrl })
    })
      .then(res => res.json())
      .then(data => {
        const risk = data.risk.toLowerCase();
        document.getElementById("result").innerHTML = `
          <p><strong>URL:</strong> ${data.url}</p>
          <p><strong>Phishing Probability:</strong> ${data.probability_phishing}</p>
          <p><strong>Risk Level:</strong> <span class="risk ${risk}">${data.risk}</span></p>
        `;
        const input = document.getElementById("manualUrl");
        input.value = "";
        input.focus();
      })
      .catch(() => {
        document.getElementById("result").textContent = "Prediction failed.";
      });
  });
});
