---
layout: default
title: Command Reference
nav_order: 3
---

# Command Reference
{: .no_toc }

Complete list of NovaChat AI bot commands and their usage.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Basic Commands

### /start
Start the bot and receive a welcome message.
```
/start
```

### /help
Display all available commands and their descriptions.
```
/help
```

## Chat Commands

### /chat
Start a conversation with the AI.
```
/chat Hello, how are you today?
```

### /clear
Clear your chat history.
```
/clear
```
Requires confirmation via inline buttons.

### /export
Export your chat history in different formats.
```
/export markdown  # Export as Markdown
/export pdf      # Export as PDF
```

## Image Generation

### /image
Generate a basic image quickly.
```
/image sunset over mountains
```

### /imagine
Create high-quality images using Together AI.
```
/imagine beautiful sunset over mountains, realistic, 4k, detailed
```

## Settings & Configuration

### /setgroqkey
Set your Groq API key for chat functionality.
```
/setgroqkey your_api_key_here
```
Note: Message will be deleted immediately for security.

### /settogetherkey
Set your Together AI key for high-quality image generation.
```
/settogetherkey your_api_key_here
```
Note: Message will be deleted immediately for security.

### /settings
View current bot settings.
```
/settings
```

### /temperature
Adjust the AI's response creativity (0.0-1.0).
```
/temperature 0.7
```

### /tokens
Set maximum response length.
```
/tokens 1024
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
