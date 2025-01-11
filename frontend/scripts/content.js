import { sensitivePatterns } from "./patterns.js";

if (window.location.hostname === "chatgpt.com") {

  const checkForInput = setInterval(() => {
    const inputContainer = document.querySelector("#prompt-textarea");
    if (inputContainer) {
      clearInterval(checkForInput);

      let isProcessing = false;
      let foundSensitiveData = false;
      let sensitiveNodes = [];
      const observer = new MutationObserver((mutations) => {
        if (isProcessing) return;
        isProcessing = true;

        mutations.forEach((mutation) => {
          if (mutation.type === "childList" && mutation.addedNodes.length) {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeName === "P") {
                const text = node.textContent;
                for (const [type, { pattern }] of Object.entries(
                  sensitivePatterns
                )) {
                  if (pattern.test(text)) {
                    foundSensitiveData = true;
                    sensitiveNodes.push({ node, text, pattern });
                  }
                }
              }
            });
          }
        });
        if (foundSensitiveData) {
          const composerContainer = document.getElementById(
            "composer-background"
          );
          composerContainer.style.border = "1px solid red";
          showWarning();
          addCleanseButton(
            inputContainer,
            sensitiveNodes,
            () => {
              foundSensitiveData = false;
              sensitiveNodes = [];
            },
            composerContainer
          );
        }

        isProcessing = false;
      });

      observer.observe(inputContainer, {
        childList: true,
        subtree: true,
      });
    }
  }, 1000);
}

function showWarning() {
  let warning = document.querySelector(".sensitive-warning");
  if (!warning) {
    warning = document.createElement("div");
    warning.className = "sensitive-warning";
    warning.style.position = "absolute";
    warning.style.top = "10px";
    warning.style.right = "10px";
    warning.style.backgroundColor = "#ab0707";
    warning.style.color = "white";
    warning.style.padding = "6px 8px";
    warning.style.borderRadius = "4px";
    warning.style.zIndex = "1000";
    document.body.appendChild(warning);
  }
  warning.textContent = `⚠️ Found sensitive data!`;
}

