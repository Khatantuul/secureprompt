import { sensitivePatterns } from "./patterns.js";

//Initial platform check only for chatgpt.com for now
if (window.location.hostname === "chatgpt.com") {

  const checkForInput = setInterval(() => {
    const inputContainer = document.querySelector("#prompt-textarea");
    if (inputContainer) {
      clearInterval(checkForInput); 

      let isProcessing = false;
      let foundSensitiveData = false;
      let sensitiveNodes = []; 
      //capturing p tag nodes with sensitive data separately to avoid mutation observer processing on every node
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
          //getting the container that holds textarea and all other buttons on chatgpt
          const composerContainer = document.getElementById(
            "composer-background"
          );
          composerContainer.style.border = "1px solid red";
          //showing extra warning on top to get attention
          showWarning();
          //passing resetState function in order to reset the foundSensitiveData flag to avoid mutation observer
          //detecting the same sensitive data again
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

function addCleanseButton(
  inputContainer,
  sensitiveNodes,
  resetState,
  composerContainer
) {
  let button = document.querySelector(".cleanse-button");
  if (!button) {
    button = document.createElement("button");
    button.className = "cleanse-button";
    button.textContent = "🧹 Cleanse Sensitive Data";
    button.style.position = "absolute";
    button.style.bottom = "10px";
    button.style.right = "60px";
    button.style.color = "white";
    button.style.padding = "6px 8px";
    button.style.borderRadius = "30px";
    button.style.border = "1px solid rgba(255, 255, 255, 0.2)";
    button.style.cursor = "pointer";
    inputContainer.parentElement.appendChild(button);

    button.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      for (const { node, text, pattern } of sensitiveNodes) {
        const newText = text.replace(pattern, "******************");
        node.textContent = newText;
      }

      resetState();

      document.querySelector(".sensitive-warning")?.remove();
      composerContainer.style.border = "none";
      const message = document.createElement("div");
      message.textContent = "✓ Replaced sensitive data with placeholders";
      message.style.position = "absolute";
      message.style.bottom = "10px";
      message.style.right = "60px";
      message.style.color = "#10a37f";
      message.style.padding = "6px 8px";

      inputContainer.parentElement.appendChild(message);
      button.remove();

      setTimeout(() => message.remove(), 6000);
    });
  }
}
