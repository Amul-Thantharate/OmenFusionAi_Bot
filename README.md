# AIFusionBot 🤖

A versatile Telegram bot that combines AI chat, image generation, voice processing, and YouTube integration.

## Latest Updates (v2.4.0) 🎉
- Improved image description using Groq's vision model
- Enhanced voice response system
- Optimized image processing pipeline
- Better error handling and user feedback
- Updated dependencies and performance improvements

## Features ✨

- **AI Chat**: Natural language conversations with Groq
- **Image Analysis**: Detailed image descriptions with voice output
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
GROQ_API_KEY=your_groq_key
TOGETHER_API_KEY=your_together_key
```

## Environment Setup 🔐

1. **Create Environment File**
```bash
cp .env.example .env
```

2. **Configure Environment Variables**
```env
# Required Variables
TELEGRAM_BOT_TOKEN=   # Get from @BotFather
GROQ_API_KEY=        # Get from https://console.groq.com/keys
TOGETHER_API_KEY=    # Get from https://www.together.ai
ROOT_PASSWORD=       # Set a secure password for admin commands

# Optional Variables
ADMIN_USER_ID=       # Your Telegram User ID
```

3. **Security Notes**
- Use a strong password for ROOT_PASSWORD
- Keep your .env file secure
- Never commit .env to version control
- Backup your credentials safely

4. **Run Bot**
```bash
python app.py
```

## Commands 📝

### General
- `/start` - Begin using bot
- `/help` - View commands
- `/chat` - Start conversation

### Media
- `/imagine` - Generate images
- `/describe` - Analyze and describe images
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
- Groq API Key (v0.4.1+)
- Together AI API Key (v0.2.8+)
- PIL (Python Imaging Library)
- gTTS (Google Text-to-Speech)

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
- Advanced image analysis with Groq Vision
- Voice descriptions of images
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
