# OmenFusionAi_Bot Documentation

OmenFusionAi_Bot is a powerful Telegram bot that combines multiple AI capabilities including chat, image generation, voice interaction, and more. Built with Python, it leverages Groq and Together AI for advanced AI features.

## Features

- 🤖 **AI Chat**: Engage in natural conversations using Groq's Mixtral model
- 🎨 **Image Generation**: Create images from text descriptions using Together AI
- 🗣️ **Voice Interaction**: Text-to-speech and speech-to-text capabilities
- 📝 **Chat History**: Save and export conversation history
- 🔊 **Audio Processing**: Handle various audio formats and YouTube video transcription
- ⚙️ **Customizable Settings**: Adjust model parameters and bot behavior

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   GROQ_API_KEY=your_groq_key
   TOGETHER_API_KEY=your_together_key
   TELEGRAM_BOT_TOKEN=your_telegram_token
   ```
4. Run the bot:
   ```bash
   python app.py
   ```

## Available Commands

### Core Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/chat` - Chat with the AI
- `/imagine` - Generate images
- `/enhance` - Enhance text prompts

### Voice & Audio
- `/voice` - Voice message settings
- `/togglevoice` - Toggle voice responses
- `/transcribe` - Transcribe audio or YouTube video
- `/formats` - Show supported audio formats
- `/lang` - Show language information

### Settings & Management
- `/settings` - View current settings
- `/clear` - Clear conversation history
- `/save` - Save chat history
- `/export` - Export chat history
- `/temperature` - Set AI temperature

### Maintenance
- `/maintenance` - Set bot maintenance mode
- `/status` - Check bot status
- `/subscribe` - Subscribe to status updates
- `/unsubscribe` - Unsubscribe from updates

## Architecture

The bot is built with a modular architecture:

- `app.py`: Main Flask application
- `main.py`: Core functionality and API integrations
- `telegram_bot.py`: Telegram bot implementation
- `image_generator.py`: Image generation utilities
- `audio_transcribe.py`: Audio processing functions
- `tone_enhancer.py`: Text enhancement utilities

## API Integrations

- **Groq AI**: Used for chat functionality with the Mixtral-8x7b model
- **Together AI**: Powers image generation capabilities
- **Google Text-to-Speech**: Provides voice response functionality

## Development

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Setting Up Development Environment
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```
2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security

- API keys are stored securely in `.env` file
- User messages containing API keys are immediately deleted
- Session data is stored in memory only
- No sensitive data is logged

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure all required API keys are set in `.env`
   - Check API key validity
   - Verify environment variables are loaded

2. **Voice Message Issues**
   - Check ffmpeg installation
   - Verify temporary directory permissions
   - Ensure enough disk space

3. **Image Generation Errors**
   - Verify Together AI API key
   - Check prompt length and content
   - Monitor API rate limits

### Getting Help

- Create an issue on GitHub
- Check existing issues for solutions
- Contact maintainers

## License

This project is licensed under the MIT License - see the LICENSE file for details.
