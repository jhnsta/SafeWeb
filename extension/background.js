chrome.runtime.onInstalled.addListener(() => {
  console.log("SafeWeb extension installed.");

  chrome.contextMenus.create({
    id: "safeweb-scan-link",
    title: "Scan with SafeWeb",
    contexts: ["link"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "safeweb-scan-link") {
    chrome.storage.local.set({ scannedLink: info.linkUrl }, () => {
      chrome.action.openPopup();
    });
  }
});
