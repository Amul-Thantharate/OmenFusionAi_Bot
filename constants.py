"""Shared constants for the OmenFusionAi_Bot."""

# File and Directory Settings
MEDIA_FOLDER = 'medias'
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB

# Command Categories 📱
COMMAND_CATEGORIES = {
    "🤖 Chat": ['chat'],
    "🎨 Image": ['imagine', 'enhance', 'describe'],
    "📽️ Video": ['analyze_video'],
    "🔧 Settings": ['settings', 'togglevoice', 'clear_chat'],
    "ℹ️ General": ['start', 'help'],
    "🔐 Admin": ['maintenance']
}

# Prompts and Templates 📝
SUMMARY_PROMPT = """
You are a YouTube video summarizer. You will take the transcript text and summarize the entire video, providing the important points within 250 words. Please provide the summary of the text given here:
"""

VIDEO_ANALYSIS_PROMPT = """
Please analyze this video and provide detailed insights about:
1. 📹 What's happening in the video
2. 👥 Key objects and people present
3. 🎬 Notable actions or events
4. 🌍 The overall context or setting

Be specific but concise in your analysis.
"""

# Help Messages 💡
HELP_MESSAGE = r"""
🤖 Welcome to OmenFusionAi_Bot! Here are the available commands:

/start - Start the bot and get a welcome message
/help - Show this help message
/insights <url> - Get detailed insights about a YouTube video
/chat - Start a chat session with the bot
/image <prompt> - Generate an image based on your prompt
/pdf <url> - Generate a PDF from a webpage
/tts <text> - Convert text to speech
/translate <text> - Translate text to English
/ocr <image> - Extract text from an image

For more information about each command, just try using it!
"""

# Error Messages ❌
ERROR_MESSAGES = {
    "video_too_large": (
        "❌ Video file is too large!\n\n"
        "Due to Telegram's limitations, I can only process videos up to 50MB.\n"
        "Please try:\n"
        "• Compressing the video\n"
        "• Trimming it to a shorter length\n"
        "• Reducing the video quality\n"
        "• Sending a shorter clip"
    ),
    "invalid_video": (
        "Please send a valid video file (MP4, MOV, AVI, etc.)\n\n"
        "📝 Requirements:\n"
        "• Maximum file size: 50MB\n"
        "• Supported formats: MP4, MOV, AVI\n"
        "• Recommended length: 1-3 minutes"
    ),
    "processing_error": (
        "❌ Error processing video content. This could be because:\n"
        "• The video is too long\n"
        "• The video format is not supported\n"
        "• The video content couldn't be processed\n\n"
        "Please try with a different video or contact support if the issue persists."
    )
}
