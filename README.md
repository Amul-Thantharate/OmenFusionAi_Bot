# AIFusionBot 🤖

A versatile Telegram bot that combines AI chat, image generation, voice processing, and YouTube integration.

## Features ✨

- **AI Chat**: Natural language conversations with OpenAI
- **Image Generation**: Create images from text descriptions
- **Voice Processing**: Speech-to-text and text-to-speech
- **YouTube Integration**: Download audio from videos
- **Maintenance System**: Schedule maintenance with notifications

## Quick Start 🚀

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/AIFusionBot.git
cd AIFusionBot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
Create `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_token
OPENAI_API_KEY=your_openai_key
TOGETHER_API_KEY=your_together_key
```

4. **Run Bot**
```bash
python telegram_bot.py
```

## Commands 📝

### General
- `/start` - Begin using bot
- `/help` - View commands
- `/chat` - Start conversation

### Media
- `/imagine` - Generate images
- `/transcribe` - Convert speech to text
- `/voice` - Convert text to speech
- `/audio` - Download YouTube audio

### Settings
- `/settings` - View configuration
- `/togglevoice` - Toggle voice responses

### Maintenance
- `/maintenance` - Set maintenance mode
- `/status` - Check bot status
- `/subscribe` - Get status updates

## Requirements 📋

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Together AI API Key

## Documentation 📚

- [Setup Guide](docs/setup.md)
- [Commands](docs/commands.md)
- [Changelog](docs/changelog.md)
- [Contributing](CONTRIBUTING.md)

## Features in Detail 🔍

### Chat System
- Natural language processing
- Context-aware responses
- Voice message support
- History management

### Image Features
- Text-to-image generation
- Image analysis
- Prompt enhancement
- Style customization

### Audio Processing
- Speech-to-text conversion
- Text-to-speech synthesis
- YouTube audio extraction
- Multiple format support

### Maintenance System
- Scheduled maintenance
- Status notifications
- Auto-recovery
- User subscriptions

## Contributing 🤝

We welcome contributions! See [Contributing Guide](CONTRIBUTING.md) for details.

## License 📄

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## Support 💬

Need help? Check our [documentation](docs/index.md) or open an issue.
