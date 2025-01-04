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

- Python 3.12 or higher
- pip (Python package installer)
- Git
- A Telegram Bot Token
- Groq API Key
- Together AI API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NovaChat-AI.git
cd NovaChat-AI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:
```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TOGETHER_API_KEY=your_together_api_key
GROQ_API_KEY=your_groq_api_key

# Optional
PORT=5000  # Port for Flask web server
DEBUG=False  # Flask debug mode
```

You can also configure API keys through the bot using:
1. `/uploadenv` command (recommended)
2. Individual commands (`/setgroqkey`, `/settogetherkey`)

### API Keys

1. **Telegram Bot Token**:
   - Create a bot with [@BotFather](https://t.me/BotFather)
   - Copy the provided token

2. **Groq API Key**:
   - Sign up at [Groq Console](https://console.groq.com)
   - Generate an API key
   The Groq API key is required for both chat functionality and image analysis. You can obtain it from [Groq Console](https://console.groq.com):

   1. Sign up for a Groq account
   2. Navigate to API Keys section
   3. Create a new API key
   4. Set the key in the bot using:
   ```
   /setgroqkey YOUR_API_KEY
   ```
   The same API key will be used for both:
   - Chat functionality with LLM models
   - Image analysis with Groq Vision API

3. **Groq Vision Setup**:
   To use Groq Vision, you need to set up a Groq Vision API key. You can do this by following these steps:
   1. Go to the Groq Console and navigate to the API Keys section
   2. Click on "Create a new API key"
   3. Select "Groq Vision" as the API type
   4. Set the key in the bot using:
   ```
   /setgroqvisionkey YOUR_API_KEY
   ```
   Note: You need to have a separate API key for Groq Vision.

3. **Together AI Key**:
   - Register at [Together AI](https://api.together.xyz)
   - Create an API key

## Development Setup

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

### Manual Deployment

Run with Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## Security Notes

- Never commit your `.env` file
- Keep API keys secure
- Use HTTPS in production
- Regularly rotate API keys

## Troubleshooting

1. **API Key Issues**:
   - Verify keys are set correctly
   - Check for spaces/newlines
   - Try `/uploadenv` command

2. **Image Generation**:
   - Ensure Together AI key is valid
   - Check API quotas
   - Verify network connectivity

3. **Chat Issues**:
   - Confirm Groq API key
   - Check response settings
   - Try clearing chat history

## Support

For issues and feature requests:
1. Check existing GitHub issues
2. Create a new issue with details
3. Follow the contribution guidelines

## Next Steps

- [Learn available commands](commands.md)
- [View changelog](changelog.md)
- [Contribute to development](https://github.com/Amul-Thantharate/AIFusionBot/blob/main/CONTRIBUTING.md)

## Video Management

### Video Download

- The bot will automatically download videos from YouTube
- Videos are stored in the `downloaded_videos/` directory

### Video Storage

- The bot will store videos in the `downloaded_videos/` directory
- You can configure the storage directory in the `.env` file

### Video Deletion

- The bot will automatically delete videos after a certain period of time
- You can configure the deletion period in the `.env` file

## Maintenance

### Regular Tasks

1. Clear downloaded videos:
```
/clear
```

2. Check storage usage:
```
/videos
```

3. Update dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### Storage Management

- Ensure sufficient disk space
- Use `/clear` to remove old videos
- Check directory permissions
