---
layout: default
title: Setup Guide
nav_order: 2
---

# Setup Guide
{: .no_toc }

Learn how to set up and deploy AIFusionBot.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git
- A Telegram account
- A bot token from [@BotFather](https://t.me/botfather)

### Required Environment Variables
Create a `.env` file in the root directory with these variables:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ROOT_PASSWORD=your_admin_password
ADMIN_USER_ID=your_admin_telegram_id
```

### Optional API Keys
Users can set these directly through the bot:
- Groq API Key (`/setgroqapi`) - Get from [Groq](https://groq.com)
- Replicate API Key (`/setreplicateapi`) - Get from [Replicate](https://replicate.com)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AIFusionBot.git
cd AIFusionBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Run the bot:
```bash
python app.py
```

## Configuration

### Environment Variables

#### Required Variables
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
- `ROOT_PASSWORD`: Password for admin operations
- `ADMIN_USER_ID`: Your Telegram user ID for admin access

#### Optional Variables
These can be set by users through bot commands:
- Groq API Key: Set via `/setgroqapi`
- Replicate API Key: Set via `/setreplicateapi`

### Security Notes
- API keys are stored in memory only
- Keys are not persisted between bot restarts
- Messages containing API keys are automatically deleted
- Admin commands are protected by user ID verification

## Server Requirements

### Minimum Requirements
- 1GB RAM
- Python 3.8+
- Stable internet connection
- 1GB free disk space

### Recommended Requirements
- 2GB RAM
- Python 3.10+
- High-speed internet connection
- 2GB free disk space
- SSL certificate (for production)

## Deployment

### Local Development
1. Follow the Quick Start guide
2. Use development environment variables
3. Run with debug logging enabled

### Production Deployment
1. Set up a production server
2. Configure SSL certificates
3. Use production environment variables
4. Set up logging
5. Configure automatic restarts

### Docker Deployment
Coming soon!

## Maintenance

### Regular Tasks
- Monitor log files
- Check disk usage
- Update dependencies
- Backup configuration

### Troubleshooting
- Check log files for errors
- Verify environment variables
- Ensure API keys are valid
- Check network connectivity

## Security Best Practices

### API Key Management
- Never share API keys
- Use bot commands to set keys
- Regularly rotate keys
- Monitor for unauthorized usage

### Bot Security
- Keep Python updated
- Update dependencies regularly
- Monitor bot activity
- Use strong admin password

### Data Protection
- No persistent storage of API keys
- Automatic message deletion for sensitive data
- Session data cleared on restart
- Secure environment variable handling
