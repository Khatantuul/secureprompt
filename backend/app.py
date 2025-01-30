"""
Flask Application Entry Point

This module serves as the main entry point for the Flask application.
It handles route configurations, middleware setup, and core application logic.

Key components:
- API endpoint for scanning sensitive data in request payload
- Initial simple regex patterns to check against
- SSL certificate configuration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re, os
from dotenv import load_dotenv
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer


load_dotenv()
ssl_keyfile = os.getenv("SSL_KEYFILE")
ssl_certfile = os.getenv("SSL_CERTFILE")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class PromptScanRequest(BaseModel):
    prompt: str

class SensitivePatternDetector:
    def __init__(self):
        self.patterns = {
        'API_KEY': [
            r'(api_key|apikey|api-key)\s*[=:]\s*[\'"][^\'"]{10,}[\'"]',
            r'sk-[a-zA-Z0-9]{48}',
            r'(APIKEY|API_KEY|ApiKey)\s*=\s*[\'"][^\'"]{10,}[\'"]'
        ],
        'AWS_CREDENTIALS': [

            r'(?:AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|aws_access_key_id|aws_session_token)\s*[=:]\s*[\'"]?[^\'"\n]+?(?=\s|$)',
        
            r'(?:AKIA|ASIA|AROA|AIDA|AGPA)[A-Z0-9]{16}(?:EXAMPLE)?(?=\s|$)',

            r'(?:aws)?_?(?:access|secret|session)_?(?:key|token|id)[^\S\r\n]*(?::|=>|=|\s)\s*[\'"]?[A-Za-z0-9/+=]{40}[\'"]?(?=\s|$)',
        
            r'[A-Za-z0-9/+=]{40}(?:EXAMPLE|KEY)?(?=\s|$)',
        ],
        'DATABASE_CONNECTION': [
            r'(?:mongodb|postgresql|mysql):\/\/[^:]+:[^@]+@(?:(?:\[[^\]]+\]|[^/?:,\s]+)(?::\d+)?(?:,[^/?:,\s]+(?::\d+)?)*?)(?:\/[^?\s]*)?(?:\?[^\s]*)?(?=\s|$)',
            r'(connection_string|connectionstring)\s*[=:]\s*[\'"][^\'"]{10,}[\'"]'
        ],
        'GITHUB_TOKEN': [
            r'ghp_[a-zA-Z0-9]{39}', 
            r'(github_token|githubtoken)\s*[=:]\s*[\'"][^\'"]{10,}[\'"]'
        ],
        'PRIVATE_KEY': [  
            r'-----BEGIN PRIVATE KEY-----[^-]+-----END PRIVATE KEY-----'
        ]
    }

    def detect_sensitive_pattern(self,prompt):
        """
        Detects sensitive patterns in the input text using predefined regex patterns

        Args:
            prompt (str): The input text to analyze for sensitive patterns
        Returns:
            list: A list of all matched sensitive patterns found in the text. Empty list if no matches. 
        """
        category_matches = []
        for _, pattern_list in self.patterns.items():         
            for pattern in pattern_list:
                matches = re.findall(pattern, prompt, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if matches:
                  
                    category_matches.extend(matches)
        return category_matches

scanner = SensitivePatternDetector()

model = AutoModelForTokenClassification.from_pretrained("./results/checkpoint-50")
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base", add_prefix_space=True)
model.eval()

def get_sensitive_parts(text, threshold=0.5):
    #tokenizing the request text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    
    # getting the model outputs
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.sigmoid(outputs.logits)
        predictions = predictions.squeeze(0)
    
    # getting tokens and their probabilities
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    probs = predictions[:, 1].numpy()  
    
    # collecting the sensitive parts that make up one sensitive phrase
    sensitive_parts = []
    current_sensitive = []
    current_prob = 0
    
    for token, prob in zip(tokens, probs):
        if token in [tokenizer.cls_token, tokenizer.sep_token, tokenizer.pad_token]:
            continue
            
        if prob > threshold:
            current_sensitive.append(token)
            current_prob = max(current_prob, prob)
        elif current_sensitive:
            sensitive_parts.append({
                "text": tokenizer.convert_tokens_to_string(current_sensitive),
                "confidence": float(current_prob)
            })
            current_sensitive = []
            current_prob = 0
    
    # if remaining sensitive parts
    if current_sensitive:
        sensitive_parts.append({
            "text": tokenizer.convert_tokens_to_string(current_sensitive),
            "confidence": float(current_prob)
        })
    
    return sensitive_parts

@app.post("/scan")
async def scan_prompt(request: PromptScanRequest):
    try:
        # catching sensitive patterns
        caught_patterns = get_sensitive_parts(request.prompt)
        
        return {
            "status": "success",
            "matches": caught_patterns,
            "found_length": len(caught_patterns)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        log_level="debug"
    )