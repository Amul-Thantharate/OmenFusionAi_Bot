# Command Reference 🛠️

## Basic Commands

### Getting Started
| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Initialize the bot | `/start` |
| `/help` | Show all available commands | `/help` |
| `/settings` | View current configuration | `/settings` |

### Chat Commands
| Command | Description | Example |
|---------|-------------|---------|
| `/chat` | Start AI conversation | `/chat What is quantum computing?` |
| `/clear` | Clear chat history | `/clear` |
| `/export` | Export chat history | `/export markdown` or `/export pdf` |

### Image Generation
| Command | Description | Example |
|---------|-------------|---------|
| `/image` | Generate basic image | `/image sunset over mountains` |
| `/imagine` | Create high-quality image | `/imagine photorealistic mountain landscape, 4k` |

## Configuration Commands

### API Keys
| Command | Description | Security |
|---------|-------------|----------|
| `/setgroqkey` | Set Groq API key | Auto-deletes message |
| `/settogetherkey` | Set Together AI key | Auto-deletes message |

### Chat Settings
| Command | Description | Range |
|---------|-------------|-------|
| `/temperature` | Set response creativity | 0.0 - 1.0 |
| `/tokens` | Set maximum response length | 1 - 4096 |

## Advanced Usage

### Chat Export Options
```bash
/export markdown  # Export as .md file
/export pdf      # Export as .pdf file
```

### Image Generation Tips
- Be specific in descriptions
- Include style preferences
- Specify quality level
- Add artistic references

Example:
```bash
/imagine beautiful mountain landscape at sunset, 
         photorealistic style, 
         dramatic lighting, 
         4k resolution
```

## Command Parameters

### Temperature
- Lower (0.1-0.3): More focused, deterministic responses
- Medium (0.4-0.7): Balanced creativity
- Higher (0.8-1.0): More creative, varied responses

### Token Length
- Short (256): Quick responses
- Medium (1024): Standard conversations
- Long (2048+): Detailed explanations

## Error Messages

### Common Errors
| Error | Meaning | Solution |
|-------|----------|----------|
| "API key required" | Missing API key | Set key with appropriate command |
| "Invalid API key" | Incorrect key format | Check key and try again |
| "Generation failed" | Image creation error | Check prompt and try again |

## Best Practices

1. **API Key Security**
   - Set keys in private chat
   - Never share keys publicly
   - Rotate keys periodically

2. **Image Generation**
   - Be specific in prompts
   - Start simple, then add detail
   - Use reference examples

3. **Chat Optimization**
   - Clear context when switching topics
   - Export important conversations
   - Adjust temperature for task type

## Command Shortcuts

Coming in future updates:
- Custom command aliases
- Keyboard shortcuts
- Quick response templates
