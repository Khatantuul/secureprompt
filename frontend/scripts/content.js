/**
 * Initializes the script to start mutation observer on the prompt textarea and handle sensitive data
 * @returns {void}
 */
const loadPatterns = async () => {

  //Initial platform check only for chatgpt.com for now
  if (window.location.hostname === "chatgpt.com") {
    const checkForInput = setInterval(() => {
      const inputContainer = document.querySelector("#prompt-textarea");
      if (inputContainer) {
        clearInterval(checkForInput);

        let isProcessing = false;
        const processedNodes = new WeakSet();
        //capturing p tag nodes with sensitive data separately to avoid mutation observer processing on every node
        const observer = new MutationObserver((mutations) => {
          if (isProcessing) return;
          isProcessing = true;
          let sensitiveNodes = [];
          mutations.forEach((mutation) => {
            if (mutation.type === "childList" && mutation.addedNodes.length) {
              mutation.addedNodes.forEach((node) => {
                if (
                  node.nodeName === "P" &&
                  !processedNodes.has(node) &&
                  !node.textContent.includes("******************")
                ) {
                  sensitiveNodes.push({ node, text: node.textContent });
                }
              });
            }
          });
          if (sensitiveNodes.length > 0 ) {
            handleSensitiveData(inputContainer, sensitiveNodes, processedNodes);
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
};

loadPatterns();

const handleSensitiveData = async (inputContainer,
  sensitiveNodes,
  processedNodes) => {
  const composerContainer = document.getElementById("composer-background");
  try {
    console.log("SENSITIVE NODES ----", sensitiveNodes);

    const results = await sendPromptForScanning(
      sensitiveNodes.map(({ text }) => text).join(" ")
    );

    if (results) {
      console.log("RESULTS ----", results.matches);
      addCleanseButton(
        inputContainer,
        sensitiveNodes,
        results.matches,
        composerContainer,
        processedNodes,
        () => {
          sensitiveNodes.forEach(({ node }) => {
            processedNodes.add(node); //marking nodes (p tag text) as processed for mutation observer
          });
        }
      );
    }else {
      // If no results, mark all nodes as safe (processed)
      sensitiveNodes.forEach(({ node }) => {
        processedNodes.add(node);
      });
    }
  } catch (error) {
    console.error("Error handling sensitive data:", error);
  }
};

/**
 * Sends the prompt to the backend for scanning for sensitive data
 * @param {string} prompt - The text to scan for sensitive content
 * @returns {Promise<Object|undefined>} Result object containing found_length if sensitive data found, undefined on error or if nothing found
 */
async function sendPromptForScanning(prompt) {
  try {
    const response = await fetch("https://127.0.0.1:8000/scan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });
    const result = await response.json();
    if (result.found_length > 0) {
      const composerContainer = document.getElementById("composer-background");
      composerContainer.style.border = "1px solid red";

      showWarning();
      return result;
    }
  } catch (error) {
    console.error("Error while scanning prompt:", error);
  }
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

/**
 * Adds a button to cleanse sensitive data when detected
 * @param {inputContainer} - The prompt textarea of AI chat applications
 * @param {sensitiveNodes} - The list of nodes containing all P tags with prompt text
 * @param {patterns} - Detected sensitive patterns
 * @param {composerContainer} - The parent container of inputContainer to highlight
 * @param {processedNodes} - The nodes that have been processed for sensitive data
 * @param {resetState}  - The callback to mark nodes as processed for mutation observer
 * @returns {void} 
 * @throws {Error} 
 */
function addCleanseButton(
  inputContainer,
  sensitiveNodes,
  patterns,
  composerContainer,
  processedNodes,
  resetState
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


      sensitiveNodes.forEach(({ node, text }) => {
        let replacedText = text;
        patterns.forEach((pattern) => {
          replacedText = replacedText.replace(pattern, "******************");
        });
        node.textContent = replacedText;
        processedNodes.add(node); 
      });

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
