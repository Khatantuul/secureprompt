# SecurePrompt: Protect Your Sensitive Data in AI Conversations

A browser extension that helps prevent accidental exposure of sensitive data when using ChatGPT and DeepSeek . The tool uses a fine-tuned CodeBERT model to detect potential API keys, credentials, and other sensitive information in code snippets before they are submitted.

## Why SecurePrompt?
In the age of AI-powered tools, developers often share code snippets that may unintentionally contain sensitive information. SecurePrompt acts as a safety net, ensuring your API keys, credentials, and other private data stay secure.

## Features
- Real-time detection of sensitive data in code snippets
- High-accuracy identification of:
    - API keys (OpenAI, AWS, etc.)
    - Database credentials
    - Private keys and tokens
    - Environment variables
    - Passwords
- Browser extension for seamless integration with ChatGPT and DeepSeek
- FastAPI backend for real-time analysis

## Architecture
- Frontend: Browser Extension (JavaScript)
- Backend: FastAPI (Python)
- ML Model: Fine-tuned CodeBERT for token classification
- Training Data: Synthetic dataset of code snippets with injected sensitive data

## Disclaimer
This tool is designed to help prevent accidental exposure of sensitive data but should not be relied upon as the sole security measure. Always review your code carefully before sharing.