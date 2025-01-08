# 🤖 AI Fusion Bot

A powerful Telegram bot that combines multiple AI capabilities including chat, image generation, video analysis, and YouTube summarization.

## 🌟 Features

### 💬 Chat
- `/chat` - Have an intelligent conversation with the bot
- Powered by Groq's advanced language models

### 🎨 Image Analysis
- 🖼️ **Interactive Image Analysis**: Send any image to get analysis options:
  - 📝 **Describe Image**: Get detailed analysis using Groq's LLaMA model
  - 🔍 **Generate Caption**: Get creative captions using Replicate
- 🎨 **Smart Image Generation**: Generate images from text descriptions
- 🔊 **Voice Descriptions**: Get voice descriptions of images (optional)

### 📽️ Video Analysis
- `/analyze_video` - Get AI insights from video content
- `youtube_summary` - Summarize YouTube videos
- Supports video files up to 50MB
- Powered by Google's Gemini Vision

### 🔧 Settings & Utilities
- `/settings` - Configure bot settings
- `/togglevoice` - Toggle voice responses
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
REPLICATE_API_KEY=your_replicate_api_key
GROQ_API_KEY=your_groq_api_key
```

3. Run the bot:
```bash
python app.py
```

## 📝 Requirements

- Python 3.8+
- Telegram Bot Token
- Google Gemini API Key
- Replicate API Key
- Groq API Key
- Internet connection

## 🛠️ Technical Details

- Uses Google's Gemini Pro for text and Gemini Vision for images/videos
- Implements efficient file handling and cleanup
- Includes error handling and user feedback
- Supports multiple file formats for videos and images

## 🔒 Security

- Environment variables for sensitive data
- Admin-only maintenance commands
- Secure file handling

## 📚 Usage Examples

### Image Analysis
1. Send any image to the bot
2. Choose from two options:
   - 📝 **Describe Image**: Get a detailed analysis of the image
   - 🔍 **Generate Caption**: Get a creative caption
3. Or use direct commands:
   - Reply to an image with `/describe` for analysis
   - Reply to an image with `/caption` for a caption

### Voice Responses
- Toggle voice responses with `/togglevoice`
- When enabled, get both text and voice descriptions

### Video Analysis
Send a video (up to 50MB) and get detailed insights about:
- What's happening in the video
- Key objects and people
- Notable actions or events
- Overall context and setting

### YouTube Summaries
youtube_summary https://youtube.com/watch?v=video_id
Get concise summaries of YouTube videos with key points and insights.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
