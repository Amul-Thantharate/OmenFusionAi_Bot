# AIFusionBot

A versatile Telegram bot powered by AI that can chat, transcribe audio, manage videos, enhance text, and generate images.

## Features

- 💬 **AI Chat**: Engage in natural conversations with AI
- 🎵 **Audio Transcription**: Convert voice messages and audio files to text
- 📺 **YouTube Integration**: Download and transcribe YouTube videos
- 🖼️ **Image Generation**: Create images from text descriptions
- ✨ **Text Enhancement**: Improve your text prompts
- 🔍 **Image Analysis**: Get detailed descriptions of images

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AIFusionBot.git
cd AIFusionBot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
```

5. Run the bot:
```bash
python main.py
```

## Key Commands

- `/start` - Begin using the bot
- `/help` - View all available commands
- `/chat` - Start a conversation
- `/transcribe` - Convert audio/video to text
- `/imagine` - Generate images
- `/enhance` - Improve text
- `/describe` - Analyze images
- `/videos` - List downloaded videos
- `/clear` - Delete saved videos

## Video Management

The bot can download and transcribe YouTube videos:

1. Download and transcribe:
```
/transcribe https://www.youtube.com/watch?v=VIDEO_ID
```

2. View downloaded videos:
```
/videos
```

3. Clear video storage:
```
/clear
```

## Documentation

Detailed documentation is available in the `docs` folder:
- [Commands Guide](docs/commands.md)
- [Setup Instructions](docs/setup.md)

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- Telegram Bot Token
- Groq API Key

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
