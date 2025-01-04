# AIFusionBot 🤖

A powerful Telegram bot that combines AI capabilities with practical features. Built with Python and powered by various AI services.

## Features 🌟

### Core Features
- 💬 Chat with AI using natural language
- 🎨 Generate and manipulate images
- 🗣️ Voice interaction (Text-to-Speech & Speech-to-Text)
- 🎵 YouTube audio download and processing
- 🔄 Maintenance mode with auto-recovery

### AI Capabilities
- Natural language chat with OpenAI GPT
- Image generation with Together AI
- Voice synthesis and recognition
- Image captioning and analysis

### System Features
- 🔔 Status notifications and subscriptions
- ⚡ Automatic maintenance mode recovery
- 📊 System status monitoring
- 💾 Chat history management

## Commands 📝

### General Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/chat` - Chat with the bot

### Image Commands
- `/imagine` - Generate an image from text
- `/enhance` - Enhance the previous prompt
- `/describe` - Generate caption for an image

### Audio Commands
- `/transcribe` - Convert speech to text
- `/voice` - Convert text to speech
- `/audio` - Download YouTube video as audio
- `/formats` - Show available audio formats
- `/lang` - Show supported languages

### Settings & Maintenance
- `/settings` - View current settings
- `/togglevoice` - Toggle voice responses
- `/maintenance` - Set maintenance mode
- `/status` - Check bot status
- `/subscribe` - Subscribe to status updates
- `/unsubscribe` - Unsubscribe from updates

## Setup 🛠️

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AIFusionBot.git
cd AIFusionBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key
TOGETHER_API_KEY=your_together_key
TELEGRAM_BOT_TOKEN=your_telegram_token
```

4. Run the bot:
```bash
python telegram_bot.py
```

## Environment Variables 🔑

Required environment variables:
- `TELEGRAM_BOT_TOKEN` - Your Telegram Bot Token
- `OPENAI_API_KEY` - OpenAI API Key
- `TOGETHER_API_KEY` - Together AI API Key

## Maintenance Mode 🔧

The bot includes a maintenance mode feature:
- Use `/maintenance <duration> <message>` to enable maintenance mode
- Duration format: `2h` (2 hours) or `30m` (30 minutes)
- Users can subscribe to status updates using `/subscribe`
- Automatic recovery after maintenance period

## Contributing 🤝

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- OpenAI for GPT API
- Together AI for image generation
- Python Telegram Bot community
- All contributors and users
