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

## Quick Start
Want to try the bot without setup? Use our live instance:
[@AIFusionCom_Bot](https://t.me/AIFusionCom_Bot)

## Self-Hosting Guide
Follow these steps if you want to host your own instance of AIFusionBot.

## Prerequisites 

- Python 3.8 or higher
- pip (Python package manager)
- Git
- A Telegram account
- Required API keys:
  - Telegram Bot Token
  - Groq API Key
  - Replicate API Key

## API Keys Required

The bot requires several API keys to function:

1. **Telegram Bot Token** (Required)
   - Get from [@BotFather](https://t.me/botfather)
   - Used for bot authentication

2. **Groq API Key** (Required)
   - Sign up at [Groq](https://www.groq.com)
   - Used for:
     - Image analysis with LLaMA model
     - Text chat functionality
     - Voice transcription

3. **Replicate API Key** (Required)
   - Sign up at [Replicate](https://replicate.com)
   - Used for:
     - Image generation with Recraft v3
     - Creative caption generation

## Installation Steps 

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/NovaChat-AI.git
cd NovaChat-AI
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Required API Keys
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
REPLICATE_API_KEY=your_replicate_api_key

# Optional Settings
ROOT_PASSWORD=your_admin_password  # For admin commands
```

### 4. Get Required API Keys

1. **Telegram Bot Token**:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command
   - Follow instructions to create bot
   - Copy the provided token

2. **Groq API Key**:
   - Sign up at [Groq](https://www.groq.com)
   - Generate an API key

3. **Replicate API Key**:
   - Sign up at [Replicate](https://replicate.com)
   - Generate an API key

### 5. Configure the Bot

1. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_token
   export GROQ_API_KEY=your_key
   export REPLICATE_API_KEY=your_key
   ```
   Or use the `.env` file as shown above.

2. Or use the bot's built-in configuration:
   ```
   /uploadenv
   ```
   Then upload your `.env` file.

### 6. Run the Bot

```bash
python telegram_bot.py
```

## Features Setup 

### Voice Features

Voice features are enabled by default. Users can:
- Toggle voice responses: `/togglevoice`
- Send voice messages for transcription
- Convert text to speech

### Image Generation

Image generation is ready to use with Replicate:
- Generate images: `/imagine <description>`
- Enhance prompts: `/enhance`
- Describe images: `/describe`

### YouTube Integration

YouTube features are ready to use:
- Download audio: `/audio <url>`
- List downloads: `/videos`
- Clear downloads: `/clear`

### Maintenance Mode

Maintenance features are available to all users:
- Set maintenance: `/maintenance <duration> <message>`
- Check status: `/status`
- Subscribe to updates: `/subscribe`

## Troubleshooting 

### Common Issues

1. **Bot Not Responding**
   - Check if bot is running
   - Verify Telegram token
   - Check maintenance status

2. **API Errors**
   - Verify API keys
   - Check API quotas
   - Ensure proper formatting

3. **Voice Features Not Working**
   - Check ffmpeg installation
   - Verify file permissions
   - Check supported formats

### Error Messages

Common error messages and solutions:

```
Error: API key not found
Solution: Set API key in .env file or using /uploadenv
```

```
Error: Could not connect to Telegram
Solution: Check internet connection and bot token
```

```
Error: File permission denied
Solution: Check directory permissions
```

## Security Considerations 

1. **API Keys**
   - Never share API keys
   - Use environment variables
   - Rotate keys regularly

2. **File Uploads**
   - Limit file sizes
   - Check file types
   - Clean up temporary files

3. **User Data**
   - Handle with care
   - Clear regularly
   - Respect privacy

## Updating the Bot 

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check for new environment variables

4. Restart the bot

## Need Help? 

- Check documentation
- Use `/help` command
- Report issues on GitHub
- Join support channel

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
