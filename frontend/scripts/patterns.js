export const sensitivePatterns = {
    openAiKey: {
      pattern: /sk-[a-zA-Z0-9]{48}/g,
      replace: "[OPENAI-KEY]",
      type: "OpenAI Key",
    },
    awsKey: {
      pattern: /AKIA[A-Z0-9]{16}/g,
      replace: "[AWS-KEY]",
      type: "AWS Key",
    },
    connectionString: {
      pattern: /(?:postgresql|mysql|mongodb):\/\/\w+:[^@\s]+@[^\s]+/g,
      replace: "[CONNECTION-STRING]",
      type: "Database Connection String",
    },
    privateKey: {
      pattern: /-----BEGIN PRIVATE KEY-----.*-----END PRIVATE KEY-----/g,
      replace: "[PRIVATE-KEY]",
    },
  };
  