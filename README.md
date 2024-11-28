# AiFusionBot - Flask Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://t.me/A_iFusion_bot)
[![Groq](https://img.shields.io/badge/Groq-Powered-orange.svg)](https://console.groq.com)
[![Together AI](https://img.shields.io/badge/Together_AI-Enabled-purple.svg)](https://api.together.xyz)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](CONTRIBUTING.md)

AIFusionBot is a cutting-edge Telegram bot that combines the power of Groq's advanced language models and Together AI's image generation capabilities. Built with Flask, it offers seamless chat interactions, stunning image creation, and upcoming video generation features. Perfect for both casual users and developers, it provides an intuitive interface for AI-powered conversations, creative image generation, and robust chat management—all within your Telegram app. Whether you're looking to have engaging conversations, create unique images, or build upon the platform, AIFusionBot offers a complete AI assistant experience.

 **Try the bot now**: [A_iFusion_bot](https://t.me/A_iFusion_bot)

## Features

- Advanced AI Chat using Groq
- Image Generation (Basic and High-Quality)
- Chat History Management
- Customizable Settings
- Export Chat History (Markdown/PDF)
- Flask Web Interface
- Webhook Support

## Commands

- `/start` - Start AIFusionBot
- `/help` - Show available commands
- `/chat` - Start AI conversation
- `/image` - Generate a basic image
- `/imagine` - Create high-quality image
- `/setgroqkey` - Set Groq API key
- `/settogetherkey` - Set Together AI key
- `/settings` - View current settings
- `/export` - Export chat history
- `/clear` - Clear chat history
- `/temperature` - Adjust response creativity
- `/tokens` - Set maximum response length

## Requirements

- Python 3.12+
- Telegram Bot Token
- Groq API Key (for chat)
- Together AI API Key (for high-quality images)
- Flask & Gunicorn (for web server)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Amul-Thantharate/AIFusionBot.git
cd AIFusionBot
```

2. Create and configure your environment file:
```bash
cp .env.example .env
# Edit .env with your tokens and API keys
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Bot

### Development Mode

```bash
flask run
```

### Production Mode

Manual Production Setup:

```bash
# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## Configuration

Set the following environment variables in your `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
TOGETHER_API_KEY=your_together_api_key
PORT=5000  # Optional, defaults to 5000
```

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Set up pre-commit hooks:
```bash
pre-commit install
```

## Architecture

- Flask web application (`app.py`)
- Telegram bot integration (`telegram_bot.py`)
- AI services integration (`main.py`)
- Gunicorn production server

## API Endpoints

- `/` - Bot status check
- `/webhook` - Telegram webhook endpoint (POST)

## Future Releases

Here's what's coming in future versions of AIFusionBot:

### Version 1.1 (Upcoming)
- Real-time chat synchronization
- Additional image generation models
- Text to video conversion (Replicate)
- Multi modal support for Chat and Image

### Version 1.2 (Planned)
- Multi-user support
- Enhanced security features
- Usage analytics dashboard
- Multi-language support

### Version 1.3 (Planned)
- Audio message processing
- Video generation capabilities
- API integration for third-party apps
- Voice message processing

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Never share your API keys
- Bot commands automatically delete messages containing API keys
- API keys are stored securely in environment variables
- HTTPS recommended for production deployment

## Support

For support, please open an issue in the GitHub repository.
