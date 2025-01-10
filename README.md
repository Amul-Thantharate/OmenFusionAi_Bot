# 🤖 AI Fusion Bot

A powerful Telegram bot that combines multiple AI capabilities including chat, image generation, video analysis, and YouTube summarization.

## 🌟 Features

### 💬 Chat
- `/chat` - Have an intelligent conversation with the bot
- Powered by Groq's advanced language models
- Context-aware conversations with memory
- Supports multiple languages

### 🎨 Image Analysis & Generation
- 🖼️ **Interactive Image Analysis**: Send any image to get analysis options:
  - 📝 **Describe Image**: Get detailed analysis using Groq's LLaMA model
  - 🔍 **Generate Caption**: Get creative captions using Replicate
- 🎨 **Smart Image Generation**: Generate images from text descriptions
- Set your own Replicate API key with `/setreplicateapi`

### 📽️ Video & YouTube Analysis
- `/analyze_video` - Get AI insights from video content
- `/summarize_youtube` - Get summaries of YouTube videos
  - Supports full videos and clips
  - Generates key points and timestamps
  - Extracts main topics and themes
- Supports video files up to 50MB
- Powered by Google's Gemini Vision

### 🔧 Settings & Utilities
- `/settings` - Configure bot settings
- `/setgroqapi` - Set your Groq API key
- `/setreplicateapi` - Set your Replicate API key
- `/clear_chat` - Clear chat history
- `/help` - View all commands

## 🚀 Try it Live!
Try the bot now: [@AIFusionCom_Bot](https://t.me/AIFusionCom_Bot)

## 🚀 Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_token
ROOT_PASSWORD=your_admin_password
ADMIN_USER_ID=your_admin_telegram_id
```

3. Run the bot:
```bash
python app.py
```

## 📝 Requirements

- Python 3.8+
- Telegram Bot Token
- Google Gemini API Key
- Internet connection
- (Optional) Groq API Key - Can be set via `/setgroqapi`
- (Optional) Replicate API Key - Can be set via `/setreplicateapi`

## 🛠️ Technical Details

- Uses Google's Gemini Pro for text and Gemini Vision for images/videos
- Implements efficient file handling and cleanup
- Includes error handling and user feedback
- Supports multiple file formats for videos and images

## 🔒 Security

- Environment variables for sensitive data
- Admin-only maintenance commands
- Secure file handling
- API keys can be set individually by each user
- API keys are stored securely in memory

## 📚 Usage Examples

### Image Analysis
1. Send any image to the bot
2. Choose from two options:
   - 📝 **Describe Image**: Get a detailed analysis of the image
   - 🔍 **Generate Caption**: Get a creative caption
3. Or use direct commands:
   - Reply to an image with `/describe` for analysis
   - Reply to an image with `/caption` for a caption

### Setting Up API Keys
1. Get your Groq API key from [Groq](https://groq.com)
2. Set it in the bot: `/setgroqapi your_api_key`
3. Get your Replicate API key from [Replicate](https://replicate.com)
4. Set it in the bot: `/setreplicateapi your_api_key`

### Video Analysis
Send a video (up to 50MB) and get detailed insights about:
- What's happening in the video
- Key objects and people
- Notable actions or events
- Overall context and setting

### Future Features
- Database for storing user data and settings
- Audio analysis
- Video summarization

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 🚀 Technical Stack

- **AI Models**:
  - Groq LLM for chat
  - Gemini Pro for text analysis
  - Gemini Vision for media analysis
  - Replicate for image generation
- **Backend**: Python 3.8+ with asyncio
- **Storage**: In-memory with Redis support
- **API Integration**: REST APIs with rate limiting
- **Security**: AES encryption for API keys

## ⚠️ Troubleshooting

Common issues and solutions:
- **API Key Issues**: Ensure keys are entered without quotes
- **Video Upload Fails**: Check file size and format
- **Rate Limits**: Wait a few minutes between requests
- **Memory Issues**: Use `/clear_chat` to reset context

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
