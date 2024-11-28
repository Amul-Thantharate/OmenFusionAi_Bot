---
layout: default
title: Setup Guide
nav_order: 2
---

# Setup Guide
{: .no_toc }

Learn how to set up and deploy NovaChat AI.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Prerequisites

Before you begin, ensure you have:

- Python 3.12 or higher
- Docker (optional, for containerized deployment)
- Telegram Bot Token
- Groq API Key (for chat)
- Together AI API Key (for high-quality images)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Amul-Thantharate/AIFusionBot.git
cd AIFusionBot
```

### 2. Set Up Environment

Create and configure your `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
TOGETHER_API_KEY=your_together_api_key

# Optional
PORT=5000
FLASK_ENV=production
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt
```

## Development Setup

### Running in Development Mode

```bash
# Set Flask environment
export FLASK_APP=app.py
export FLASK_ENV=development

# Run Flask development server
flask run
```

### Setting Up Pre-commit Hooks

```bash
pre-commit install
```

## Production Deployment

### Using Docker (Recommended)

1. Build and start containers:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop services:
```bash
docker-compose down
```

### Manual Deployment

Run with Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## Telegram Bot Setup

1. Create a new bot:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Copy the provided token

2. Set webhook URL (replace with your domain):
```bash
curl -F "url=https://your-domain.com/webhook" \
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
```

## API Keys Setup

### Groq API Key

1. Visit [Groq Cloud Console](https://console.groq.com)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new key
5. Use `/setgroqkey` command in your bot

### Together AI Key

1. Go to [Together AI](https://together.ai)
2. Sign up or log in
3. Access API section
4. Create new API key
5. Use `/settogetherkey` command in your bot

## Security Considerations

1. **API Keys**:
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys periodically

2. **Production Deployment**:
   - Use HTTPS
   - Set up proper firewalls
   - Keep dependencies updated

3. **Bot Security**:
   - Implement rate limiting
   - Validate all user inputs
   - Monitor bot activity

## Troubleshooting

### Common Issues

1. **Bot Not Responding**:
   - Check if the bot is running
   - Verify webhook URL
   - Check error logs

2. **API Errors**:
   - Validate API keys
   - Check API quotas
   - Review error messages

3. **Docker Issues**:
   - Verify Docker installation
   - Check container logs
   - Ensure ports are available

### Getting Help

- Check [GitHub Issues](https://github.com/Amul-Thantharate/AIFusionBot/issues)
- Review error logs
- Contact support team

## Next Steps

- [Learn available commands](commands.md)
- [View changelog](changelog.md)
- [Contribute to development](https://github.com/Amul-Thantharate/AIFusionBot/blob/main/CONTRIBUTING.md)
