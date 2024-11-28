# NovaChat AI 

A powerful Telegram bot that combines Groq's language model and Together AI's image generation capabilities.

## Features

- Advanced AI Chat using Groq
- High-Quality Image Generation with Together AI
- Chat History Management
- Customizable Settings
- Export Chat History (Markdown/PDF)
- Flask Web Interface
- Webhook Support

## Commands

- `/start` - Start NovaChat AI
- `/help` - Show available commands
- `/chat` - Start AI conversation
- `/imagine` - Generate high-quality images
- `/setgroqkey` - Set Groq API key
- `/settogetherkey` - Set Together AI key
- `/settings` - View current settings
- `/export` - Export chat history
- `/clear` - Clear chat history
- `/temperature` - Adjust response creativity
- `/tokens` - Set maximum response length
- `/uploadenv` - Upload .env file to set API keys

## Requirements

- Python 3.12+
- Telegram Bot Token
- Groq API Key (for chat)
- Together AI API Key (for image generation)
- Flask & Gunicorn (for web server)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NovaChat-AI.git
cd NovaChat-AI
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

## Configuration

Set the following environment variables in your `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
TOGETHER_API_KEY=your_together_api_key
```

You can also use the `/uploadenv` command in Telegram to set your API keys securely.

## Running the Bot

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## Security Features

- Secure API key management
- Immediate deletion of uploaded configuration files
- In-memory file processing
- Session-based user settings

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
