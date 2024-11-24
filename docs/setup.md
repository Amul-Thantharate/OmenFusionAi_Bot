# 🚀 Setup Guide

## Prerequisites

Before setting up NovaChat AI, ensure you have:

- Python 3.8 or higher installed
- A Telegram account
- Access to the required API services

## 🔑 Getting Required API Keys

### 1. Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the provided API token
5. Keep this token secure!

### 2. Groq API Key (For AI Chat)
1. Visit [Groq Cloud Console](https://console.groq.com)
2. Create an account or sign in
3. Navigate to API Keys section
4. Click "Create New API Key"
5. Copy your API key
6. Use `/setgroqkey your_key_here` in NovaChat AI

### 3. Together AI Key (For Image Generation)
1. Go to [Together AI Platform](https://together.ai)
2. Sign up for an account
3. Go to API section
4. Generate a new API key
5. Copy the key
6. Use `/settogetherkey your_key_here` in NovaChat AI

### 4. Replicate API Key (Coming in v1.1)
1. Visit [Replicate](https://replicate.com)
2. Create an account
3. Go to Account Settings
4. Find API Tokens section
5. Generate new token
6. Save for upcoming video generation feature

## 🛠️ Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NovaChat-AI.git
cd NovaChat-AI
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` file with your tokens:
```ini
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
APP_URL=your_app_url_here

# Optional - AI Service API Keys
GROQ_API_KEY=your_groq_api_key_here
TOGETHER_API_KEY=your_together_api_key_here
```

## 🚀 Running the Bot

1. Start the bot:
```bash
python app/main.py
```

2. Open Telegram and search for your bot's username
3. Start chatting with `/start` command

## 🔧 Configuration Options

### AI Parameters
- Temperature: Controls response creativity (0.0-1.0)
- Max Tokens: Sets response length limit
- Model Selection: Choose between available AI models

### Chat Settings
- History retention
- Export formats
- Response styles

## 🔒 Security Notes

- Never share your API keys
- Use environment variables for sensitive data
- Keep your `.env` file secure
- Regularly rotate API keys

## ⚠️ Troubleshooting

### Common Issues

1. Bot not responding
   - Check if bot is running
   - Verify Telegram token
   - Check internet connection

2. API errors
   - Verify API keys
   - Check API service status
   - Confirm quota limits

3. Installation problems
   - Update pip
   - Check Python version
   - Verify dependencies

## 📞 Support

Need help? Try these resources:
- Check [Command Reference](commands.md)
- View [Changelog](changelog.md)
- Create an issue on GitHub

## 🔄 Updating

To update NovaChat AI:

1. Pull latest changes:
```bash
git pull origin main
```

2. Update dependencies:
```bash
pip install -r requirements.txt --upgrade
```

3. Check changelog for breaking changes
