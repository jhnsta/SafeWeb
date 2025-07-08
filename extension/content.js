chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getPageData") {
    const html = document.documentElement.outerHTML;
    const url = window.location.href;
    sendResponse({ html: html, url: url });
  }
});
