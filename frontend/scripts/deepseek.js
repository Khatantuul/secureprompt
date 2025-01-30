/**
 * Loads script to start detection on the prompt textarea and handle sensitive data
 * @returns {void}
 */
const loadDeepseek = async () => {
   
    //Initial platform check for chat.deepseek.com
    if (window.location.hostname === "chat.deepseek.com") {
      const checkForInput = setInterval(() => {
        const inputContainer = document.querySelector(".fad49dec");
        if (inputContainer) {
          clearInterval(checkForInput);

          inputContainer.addEventListener("paste", (e) => {
            setTimeout(() => { 
              const text = document.querySelector(".b13855df")?.textContent.trim();
              handleSensitiveDataDeepseek(inputContainer, text);
            }, 100);
          });
          
        }
      }, 1000);
    }
  };
  
  loadDeepseek();
  
  const handleSensitiveDataDeepseek = async (inputContainer, prompt) => {
    const composerContainer = document.querySelector(".cefa5c26");
    try {  
      const results = await sendPromptForScanningDeepseek(
        prompt
      );
  
      if (results) {
        console.log("RESULTS ----", results.matches);
        addCleanseButtonDeepseek(
          inputContainer,
          results.matches,
          composerContainer,      
        );
      }
    } catch (error) {
      console.error("Error handling sensitive data:", error);
    }
  };
  
//   /**
//    * Sends the prompt to the backend for scanning for sensitive data
//    * @param {string} prompt - The text to scan for sensitive content
//    * @returns {Promise<Object|undefined>} Result object containing found_length if sensitive data found, undefined on error or if nothing found
//    */
  async function sendPromptForScanningDeepseek(prompt) {
    console.log("Prompt to scan:", prompt);
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
        const composerContainer = document.querySelector(".cefa5c26");
        composerContainer.style.border = "1px solid red";
  
        showWarning();
        return result;
      }
    } catch (error) {
      console.error("Error while scanning prompt:", error);
    }
  }
  
//   /**
//    * Adds a button to cleanse sensitive data when detected
//    * @param {inputContainer} - The prompt textarea of AI chat applications
//    * @param {sensitiveNodes} - The list of nodes containing all P tags with prompt text
//    * @param {patterns} - Detected sensitive patterns
//    * @param {composerContainer} - The parent container of inputContainer to highlight
//    * @param {processedNodes} - The nodes that have been processed for sensitive data
//    * @param {resetState}  - The callback to mark nodes as processed for mutation observer
//    * @returns {void} 
//    * @throws {Error} 
//    */
  function addCleanseButtonDeepseek(
    inputContainer,
    patterns,
    composerContainer,
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
        
        const text = document.querySelector(".b13855df")?.textContent.trim();
        const container = document.getElementById("chat-input");
        let replacedText = '';

        replacedText = text.split("\n")
        .map(line => {
            let modifiedLine = line;
            patterns.forEach(pattern => {
                
                modifiedLine = (pattern.confidence > 0.7) ? modifiedLine.replace(pattern.text, "*****") : modifiedLine;
            });
            return modifiedLine;
        })
        .join("\n");
         container.value = replacedText;
          
  
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
  
        setTimeout(() => message.remove(), 7000);
      
      });
    }
  }
  