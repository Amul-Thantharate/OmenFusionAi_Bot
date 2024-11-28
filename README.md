# AiFusionBot - Flask Telegram Bot

A powerful Flask-based Telegram bot powered by Groq and Together AI for chat and image generation.

## Features

- 🤖 Advanced AI Chat using Groq
- 🎨 Image Generation (Basic and High-Quality)
- 💾 Chat History Management
- 🔧 Customizable Settings
- 📤 Export Chat History (Markdown/PDF)
- 🌐 Flask Web Interface
- 🔄 Webhook Support

## Commands

- `/start` - Start NovaChat AI
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
# Run Flask development server
flask run
```

### Production Mode

Using Docker (recommended):

1. Build and run with docker-compose:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Check container status:
```bash
docker-compose ps
```

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
- Docker containerization

## API Endpoints

- `/` - Bot status check
- `/webhook` - Telegram webhook endpoint (POST)

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
