---
layout: default
title: Command Reference
nav_order: 3
---

# NovaChat AI v2.0 Commands
{: .no_toc }

This document details all available commands and their usage in NovaChat AI v2.0.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Core Commands

### /start
Initializes NovaChat AI v2.0 and displays welcome message with available features.
```
/start
```

### /help
Shows comprehensive list of commands and features with detailed descriptions.
```
/help
```

## Chat Commands

### /chat
Initiates conversation with advanced Groq LLM models.
```
/chat Explain quantum computing
```

### /enhance
Improves the tone and style of the previous message using advanced language models.
```
/enhance
```

## Image Generation

### /imagine
Creates high-quality images using latest AI models with enhanced prompt engineering.
```
/imagine A cyberpunk city at sunset with neon signs
```

## Configuration Commands

### /setgroqkey
Configures Groq API key for LLM access.
```
/setgroqkey your_api_key_here
```

### /settogetherkey
Sets Together AI key for image generation.
```
/settogetherkey your_api_key_here
```

### /settings
Views and manages current bot configuration.
```
/settings
```

## Response Customization

### /temperature
Adjusts response creativity level (0.1-1.0).
```
/temperature 0.8
```

### /tokens
Sets maximum response length for better control.
```
/tokens 2048
```

## History Management

### /export
Exports complete chat history in chosen format.
```
/export pdf
```

### /clear
Clears current chat history and starts fresh.
```
/clear
```

## Security

### /uploadenv
Securely uploads configuration file with API keys.
```
/uploadenv
# Then attach your .env file
```

## Response Examples

### Chat Response
```
You: /chat What is artificial intelligence?

🤖 AI: Artificial Intelligence (AI) refers to computer systems designed to perform tasks that typically require human intelligence. These tasks include:

1. Learning from experience
2. Understanding natural language
3. Recognizing patterns
4. Making decisions
5. Solving complex problems

AI systems can range from rule-based programs to sophisticated deep learning models.
```

### Image Generation
```
You: /imagine beautiful sunset at beach, realistic, 4k

🎨 Generating your high-quality image with Together AI... Please wait.

[Image appears]
✨ Generated with Together AI:
beautiful sunset at beach, realistic, 4k

⏱️ Image generated in 5.23 seconds
```

## Error Handling

Common error messages and their solutions:

1. **API Key Not Set**
```
⚠️ Please set your API key first using:
/setgroqkey your_api_key
```

2. **Invalid API Key**
```
❌ Invalid API key. Please check your key and try again.
```

3. **Rate Limit**
```
⚠️ Rate limit reached. Please try again later.
```

## Best Practices

1. **Chat Commands**
   - Be specific in your requests
   - Use clear, concise language
   - Check response temperature for desired creativity

2. **Image Generation**
   - Provide detailed descriptions
   - Specify desired style and quality
   - Use appropriate keywords

3. **API Keys**
   - Never share your API keys
   - Set keys in private messages
   - Rotate keys periodically

## Command Categories

### Essential
- `/start`
- `/help`
- `/chat`
- `/image`

### Advanced
- `/imagine`
- `/export`
- `/settings`
- `/temperature`

### Configuration
- `/setgroqkey`
- `/settogetherkey`
- `/tokens`

### Management
- `/clear`
- `/export`

## Tips & Tricks

1. **Better Chat Responses**
   - Adjust temperature for creativity
   - Use context in conversations
   - Be specific in questions

2. **Quality Images**
   - Add style descriptors
   - Specify resolution
   - Include artistic elements

3. **Efficient Usage**
   - Export chats regularly
   - Clear history when needed
   - Monitor API usage
