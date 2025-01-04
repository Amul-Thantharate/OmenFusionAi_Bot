---
layout: default
title: AIFusionBot Documentation
nav_order: 1
description: "AIFusionBot - A Flask-based Telegram Bot powered by Groq and Together AI"
permalink: /
---

# AIFusionBot Documentation

Welcome to the AIFusionBot documentation! This guide will help you understand and use all the features of our Telegram bot.

## Overview

AIFusionBot is a versatile Telegram bot that combines multiple AI capabilities:
- Natural language chat using Groq's Mixtral-8x7b model
- Image generation with Together AI
- Voice interaction with text-to-speech
- YouTube audio processing
- Maintenance and monitoring

## Key Features

### AI Chat
- Powered by Groq's Mixtral-8x7b model
- Natural language understanding
- Context-aware conversations
- Customizable response parameters
- Voice response support

### Image Generation
- High-quality image creation
- Prompt enhancement
- Style customization
- Image analysis and description

### Voice & Audio
- Text-to-speech responses
- Audio file transcription
- YouTube video processing
- Multiple format support

### Management
- Chat history export
- Maintenance mode
- Status monitoring
- User subscriptions

## Quick Start

1. **Installation**
   ```bash
   git clone https://github.com/yourusername/AIFusionBot.git
   cd AIFusionBot
   pip install -r requirements.txt
   ```

2. **Configuration**
   Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_groq_key
   TOGETHER_API_KEY=your_together_key
   TELEGRAM_BOT_TOKEN=your_telegram_token
   ```

3. **Run the Bot**
   ```bash
   python app.py
   ```

## Basic Usage

1. Start a chat with the bot on Telegram
2. Use `/help` to see available commands
3. Try basic commands:
   - `/chat Hello` - Start a conversation
   - `/imagine sunset` - Generate an image
   - `/describe` - Analyze an image

## Advanced Features

### Voice Responses
- Toggle with `/togglevoice`
- Automatic text-to-speech
- Multiple language support

### Image Generation
- Enhanced prompts
- Style customization
- Image analysis

### Chat Management
- Export history
- Clear conversations
- Adjust AI parameters

## Security

- Secure API key storage
- Environment variable protection
- Message encryption
- Safe file handling

## Support

Need help? Try these resources:
- Check the [Commands](./commands) page
- View the [Changelog](./changelog)
- Read [Setup Guide](./setup)
- Join our [Telegram Group](https://t.me/aifusionbot_support)

## Contributing

We welcome contributions! See our [GitHub repository](https://github.com/yourusername/AIFusionBot) for:
- Issue reporting
- Feature requests
- Pull requests
- Code reviews

## License

AIFusionBot is open source software licensed under the MIT license.
