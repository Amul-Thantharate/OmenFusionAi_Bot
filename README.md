# AIFusionBot - Telegram Audio Transcription Bot

Created by Amul Thantharate 👋

## Features

### 🎵 Audio Transcription
- Transcribes English audio to text
- Supports multiple audio formats
- Voice messages and audio files
- Real-time progress updates
- Smart language detection

### 🤖 AI Chat
- Natural language conversations
- Adjustable response creativity
- Chat history management
- Export conversations

### 🎨 Image Generation
- Create AI-generated images
- Prompt enhancement
- Image analysis and description

### 🎤 Text-to-Speech Functionality
- The bot can now convert text responses into audio messages.
- Use the `/chat` command to receive voice messages along with text responses.
- Voice responses can be toggled on or off with the `/togglevoice` command.

### 📸 Image Description
- The bot can analyze images and provide detailed descriptions.
- Use the `/describe` command to send an image and receive a description in text and voice formats.

## Supported Audio Formats
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- OGG (.ogg, .oga)
- OPUS (.opus)
- MP4 (.mp4)
- MPEG (.mpeg, .mpga)
- WEBM (.webm)

## Commands
### General
- `/start` - Start the bot
- `/help` - Show all commands

### Audio Commands
- `/transcribe` - Convert English audio to text
- `/formats` - Show supported formats
- `/voice` - Voice message guide
- `/audio` - Audio file guide
- `/lang` - Language support info
- `/togglevoice` - Toggle voice responses on/off

### Chat Commands
- `/chat` - Start AI conversation
- `/enhance` - Enhance the provided text
- `/temperature` - Adjust creativity
- `/tokens` - Set response length
- `/clear` - Clear chat history
- `/save` - Save chat history
- `/export` - Export as file

### Image Commands
- `/describe` - Analyze an image and provide a description
- `/imagine` - Generate images from prompts
- `/enhance` - Enhance prompts
- `/describe` - Analyze images

### Settings
- `/settings` - Bot configuration
- `/uploadenv` - Configure API keys

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AIFusionBot.git
cd AIFusionBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
```

4. Run the bot:
```bash
python main.py
```

## Requirements
- Python 3.8+
- Telegram Bot Token
- Groq API Key
- Internet connection

## Best Practices
- Use clear audio quality
- Speak English clearly
- Minimize background noise
- Use supported formats only
- Keep files under 20MB

## License
MIT License - See LICENSE file for details

## Author
Created by Amul Thantharate

## Support
For issues and feature requests, please create an issue on GitHub.
