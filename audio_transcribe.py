import os
import logging
import tempfile
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create temp directory for audio files
TEMP_DIR = Path(tempfile.gettempdir()) / "audio_transcribe"
TEMP_DIR.mkdir(exist_ok=True)

# Supported audio formats
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.oga', '.opus', '.mp4', '.mpeg', '.mpga', '.webm'}

def get_file_extension(file_name: str) -> str:
    """Get the file extension from the file name."""
    return Path(file_name).suffix.lower()

def is_supported_format(file_name: str) -> bool:
    """Check if the file format is supported."""
    return get_file_extension(file_name) in SUPPORTED_FORMATS

def transcribe_audio(filename, prompt=None):
    # Initialize the Groq client
    client = Groq()  # Make sure GROQ_API_KEY is set in your environment variables
    
    try:
        # Open the audio file
        with open(filename, "rb") as file:
            # Create a translation of the audio file
            translation = client.audio.translations.create(
                file=(filename, file.read()),  # Required audio file
                model="whisper-large-v3",  # Required model to use for translation
                prompt=prompt or "Specify context or spelling",  # Optional
                response_format="json",  # Optional
                temperature=0.0  # Optional
            )
            return translation.text
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Hi! I'm your Audio Transcription Bot!\n\n"
        "I can help you convert audio to text. Here's what I can do:\n"
        "• Convert voice messages to text\n"
        "• Transcribe audio files\n\n"
        "Supported formats: MP3, WAV, M4A, OGG, OPUS, MP4, WEBM\n\n"
        "Just send me any voice message or audio file to get started!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🎯 *How to use this bot:*

1️⃣ *Send Voice Message:*
   • Click the microphone icon
   • Record your message
   • Send it to me

2️⃣ *Send Audio File:*
   • Select a file from your device
   • Make sure it's in a supported format
   • Send it to me

3️⃣ *Supported Formats:*
   • Voice Messages (OGG)
   • Audio Files (MP3, WAV, M4A, OGG, OPUS, MP4, WEBM)

4️⃣ *Commands:*
   • /start - Start the bot
   • /help - Show this help message
   • /formats - Show supported formats

⚠️ *Note:* Maximum file size is 20MB
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def formats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show supported audio formats."""
    formats_text = (
        "📝 *Supported Audio Formats:*\n\n"
        "• MP3 (.mp3)\n"
        "• WAV (.wav)\n"
        "• M4A (.m4a)\n"
        "• OGG (.ogg, .oga)\n"
        "• OPUS (.opus)\n"
        "• MP4 (.mp4)\n"
        "• MPEG (.mpeg, .mpga)\n"
        "• WEBM (.webm)\n\n"
        "✨ Just send me any audio file in these formats!"
    )
    await update.message.reply_text(formats_text, parse_mode='Markdown')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio messages."""
    try:
        # Send initial processing message
        processing_msg = await update.message.reply_text(
            "🎵 Receiving your audio...",
            parse_mode='Markdown'
        )

        # Get the audio file
        if update.message.voice:
            file = await update.message.voice.get_file()
            file_name = f"voice_{update.message.from_user.id}.ogg"
        elif update.message.audio:
            file = await update.message.audio.get_file()
            file_name = update.message.audio.file_name
            if not is_supported_format(file_name):
                await processing_msg.edit_text(
                    f"❌ Sorry, the format {get_file_extension(file_name)} is not supported.\n"
                    "Use /formats to see supported formats."
                )
                return
        else:
            await processing_msg.edit_text("❌ Please send a voice message or audio file.")
            return

        # Create unique file path
        file_path = TEMP_DIR / f"{update.message.from_user.id}_{file_name}"
        
        # Download the file
        await file.download_to_drive(str(file_path))
        
        # Update processing message
        await processing_msg.edit_text("🔄 Processing your audio... Please wait.")

        # Transcribe the audio
        transcription = transcribe_audio(str(file_path))

        if transcription:
            # Split long messages if needed (Telegram has a 4096 character limit)
            max_length = 4000
            messages = [transcription[i:i+max_length] for i in range(0, len(transcription), max_length)]
            
            # Send transcription
            await processing_msg.edit_text("✅ Transcription completed!")
            for i, msg in enumerate(messages, 1):
                if len(messages) > 1:
                    header = f"*Part {i}/{len(messages)}:*\n\n"
                else:
                    header = "*Transcription:*\n\n"
                await update.message.reply_text(f"{header}{msg}", parse_mode='Markdown')
        else:
            await processing_msg.edit_text(
                "❌ Sorry, I couldn't transcribe the audio. Please try again."
            )

        # Clean up the temporary file
        if file_path.exists():
            file_path.unlink()

    except Exception as e:
        logger.error(f"Error handling audio: {str(e)}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again later."
        )

def main() -> None:
    """Start the bot."""
    # Get the token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("formats", formats_command))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    # Run the bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
