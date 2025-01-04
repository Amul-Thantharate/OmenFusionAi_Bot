from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging
import os
import tempfile
from pathlib import Path
from datetime import datetime
from io import BytesIO
import time
import json
from dotenv import load_dotenv
from main import interactive_chat, save_chat_history, generate_image
from flask import Flask, request, jsonify
from groq import Groq
import asyncio
from gtts import gTTS
from youtube_utils import (
    download_and_compress_video,
    clear_videos,
    get_downloaded_videos
)
from tone_enhancer import ToneEnhancer

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create temp directory for files
TEMP_DIR = Path(tempfile.gettempdir()) / "aifusionbot_temp"
TEMP_DIR.mkdir(exist_ok=True, parents=True)

# Global variable for user sessions
user_sessions = {}

# Dictionary of available commands and their descriptions
COMMANDS = {
    'start': 'Start the bot',
    'help': 'Show this help message',
    'chat': 'Chat with the bot',
    'imagine': 'Generate an image from text',
    'enhance': 'Enhance the previous prompt',
    'describe': 'Generate caption for an image',
    'transcribe': 'Convert speech to text',
    'voice': 'Convert text to speech',
    'audio': 'Download YouTube video as audio',
    'formats': 'Show available audio formats',
    'lang': 'Show supported language (English only)',
    'togglevoice': 'Toggle voice responses on/off',
    'videos': 'List downloaded videos',
    'clear': 'Clear all downloaded videos',
    'maintenance': 'Set bot maintenance mode',
    'status': 'Check bot status',
    'subscribe': 'Subscribe to bot status updates',
    'unsubscribe': 'Unsubscribe from bot status updates',
    'setgroqkey': 'Set Groq API key'
}

class UserSession:
    def __init__(self):
        self.conversation_history = []
        self.last_response = None
        self.last_image_prompt = None
        self.last_image_url = None
        self.selected_model = "mistral-7b-instruct"
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.together_api_key = os.getenv('TOGETHER_API_KEY')
        self.last_enhanced_prompt = None
        self.voice_response = True

BOT_STATUS = {
    "is_maintenance": False,
    "maintenance_message": "",
    "maintenance_start": None,
    "maintenance_end": None,
    "is_online": True,
    "last_offline_message": None,
    "notified_users": set()
}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 *Welcome to AIFusionBot!*\n\n"
        "Created By Amul Thantharate👋 \n\n"
        "I'm your AI assistant with multiple capabilities:\n\n"
        "🤖 *AI Chat*\n"
        "• Use /chat to start a conversation\n"
        "• Adjust settings with /settings\n\n"
        "🎨 *Image Generation*\n"
        "• Create images with /imagine\n"
        "• Enhance prompts with /enhance\n\n"
        "🎵 *Audio Transcription*\n"
        "• Convert English audio to text\n"
        "• Use /transcribe for help\n"
        "• Check formats with /formats\n\n"
        "📷 *Image Analysis*\n"
        "• Analyze images with /describe\n"
        "• Send images directly for analysis\n\n"
        "Use /help to see all available commands!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_message = "Here are the available commands:\n\n"
    
    # Organize commands by category
    categories = {
        "💬 Chat Commands": ['chat'],
        "🎨 Image Commands": ['imagine', 'enhance', 'describe'],
        "🎵 Audio Commands": ['transcribe', 'formats', 'voice', 'audio', 'lang'],
        "⚙️ Settings": ['settings', 'uploadenv', 'togglevoice'],
        "ℹ️ General": ['start', 'help'],
        "🔧 Maintenance": ['maintenance', 'status', 'subscribe', 'unsubscribe']
    }
    
    for category, cmd_list in categories.items():
        help_message += f"\n{category}:\n"
        for cmd in cmd_list:
            if cmd in COMMANDS:
                help_message += f"/{cmd} - {COMMANDS[cmd]}\n"
    
    await update.message.reply_text(help_message)

async def setgroqkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /setgroqkey command."""
    # Delete the message containing the API key for security
    await update.message.delete()

    if not context.args:
        await update.message.reply_text(
            "Please provide your Groq API key after /setgroqkey\n"
            "Example: `/setgroqkey your_api_key`\n"
            "⚠️ Your message will be deleted immediately for security.",
            parse_mode='Markdown'
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()

    session = user_sessions[user_id]
    session.groq_api_key = context.args[0]

    await update.message.reply_text(
        "✅ Groq API key set successfully!\n"
        "You can now use all chat features.\n"
        "Try `/chat Hello!`",
        parse_mode='Markdown'
    )

async def settogetherkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /settogetherkey command."""
    # Delete the message containing the API key for security
    await update.message.delete()

    if not context.args:
        await update.message.reply_text(
            "Please provide your Together API key after /settogetherkey\n"
            "Example: `/settogetherkey your_api_key`\n"
            "⚠️ Your message will be deleted immediately for security.",
            parse_mode='Markdown'
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()

    session = user_sessions[user_id]
    session.together_api_key = context.args[0]

    # Send confirmation in private message
    await update.message.reply_text(
        "✅ Together API key set successfully!\n"
        "Try generating an image with `/imagine beautiful sunset`",
        parse_mode='Markdown'
    )

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /chat command."""
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()
            
        session = user_sessions[user_id]
        
        if not session.groq_api_key:
            await update.message.reply_text(
                "Please set your Groq API key first using the /setgroqkey command"
            )
            return
            
        # Get the message text after the /chat command
        message = ' '.join(context.args) if context.args else "Hello! How can I help you today?"
        
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
        
        # Get AI response with proper API key
        response = interactive_chat(
            text=message,
            model_type="mistral-7b-instruct",
            api_key=session.together_api_key
        )
        
        # Send text response
        await update.message.reply_text(response)
        
        # Handle voice response
        try:
            # Send recording action to show progress
            await context.bot.send_chat_action(chat_id=update.message.chat_id, action="record_voice")
            status_message = await update.message.reply_text("🎙️ Converting text to speech...")
            
            # Create voice file
            voice_path = os.path.join(tempfile.gettempdir(), f'response_{user_id}.mp3')
            success = await text_to_speech_chunk(response, voice_path)
            
            if success and os.path.exists(voice_path):
                # Update status
                await status_message.edit_text("📤 Sending voice message...")
                
                # Send the voice message
                with open(voice_path, 'rb') as voice:
                    await update.message.reply_voice(
                        voice=voice,
                        caption="🎙️ Voice Message"
                    )
                
                # Clean up
                os.remove(voice_path)
                await status_message.delete()
            else:
                await status_message.edit_text("❌ Could not generate voice message.")
            
        except Exception as voice_error:
            logger.error(f"Voice message error: {str(voice_error)}")
            await update.message.reply_text("Note: Voice message could not be generated.")
            
    except Exception as e:
        logger.error(f"Error in chat_command: {str(e)}")
        await update.message.reply_text(
            "Sorry, I encountered an error. Please try again or check your input."
        )

async def imagine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /imagine command for image generation with prompt enhancement."""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "Please provide a description after /imagine\n"
            "Example: `/imagine beautiful sunset over mountains, realistic, 4k, detailed`",
            parse_mode='Markdown'
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()

    session = user_sessions[user_id]
    if not session.together_api_key:
        await update.message.reply_text(
            "⚠️ Please set your Together API key first using:\n"
            "`/settogetherkey your_api_key`",
            parse_mode='Markdown'
        )
        return

    prompt = ' '.join(context.args)

    # Send a message indicating that prompt enhancement has started
    progress_message = await update.message.reply_text(
        "🎨 Step 1/2: Enhancing your prompt... Please wait."
    )

    try:
        start_time = time.time()
        # Pass the user_id to generate_image
        success, image_bytes, message, enhanced_prompt = generate_image(prompt, user_id=user_id)
        total_time = time.time() - start_time
        
        if success and image_bytes:
            # Update progress message for image generation
            await progress_message.edit_text("🎨 Step 2/2: Generating image from enhanced prompt...")
            
            # Use the returned enhanced prompt
            enhanced_caption = (
                f"🎯 Original prompt:\n'{prompt}'\n\n"
                f"✨ Enhanced prompt:\n'{enhanced_prompt}'\n\n"
                f"⏱️ Total generation time: {total_time:.2f} seconds"
            )
            
            # Send the generated image with the enhanced caption
            await update.message.reply_photo(
                photo=BytesIO(image_bytes),
                caption=enhanced_caption,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ Failed to generate image: {message}")
    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong while generating the image. Please try again later."
        )
    finally:
        # Delete the progress message
        await progress_message.delete()

async def enhance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /enhance command for text enhancement."""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "Please provide text after /enhance\n"
            "Example: `/enhance A boy playing basketball`",
            parse_mode='Markdown'
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()

    session = user_sessions[user_id]
    if not session.together_api_key:
        await update.message.reply_text(
            "⚠️ Please set your Together API key first using:\n"
            "`/settogetherkey your_api_key`",
            parse_mode='Markdown'
        )
        return

    text = ' '.join(context.args)

    # Send a message indicating that enhancement has started
    progress_message = await update.message.reply_text(
        "✍️ Enhancing your text... Please wait."
    )

    try:
        from tone_enhancer import ToneEnhancer
        enhancer = ToneEnhancer()
        
        # Set the API key from session
        enhancer.together_api_key = session.together_api_key
        
        start_time = time.time()
        success, enhanced_text, error = await enhancer.enhance_text(text)
        total_time = time.time() - start_time
        
        if success and enhanced_text:
            response = (
                f"🎯 Original text:\n`{text}`\n\n"
                f"✨ Enhanced version:\n`{enhanced_text}`\n\n"
                f"⏱️ Enhanced in {total_time:.2f} seconds"
            )
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            error_msg = f"❌ Failed to enhance text: {error}"
            logger.error(error_msg)
            await update.message.reply_text(error_msg)
    except Exception as e:
        error_msg = f"Error in text enhancement: {str(e)}"
        logger.error(error_msg)
        await update.message.reply_text(
            "❌ Sorry, something went wrong while enhancing the text. Please try again later."
        )
    finally:
        # Delete the progress message
        await progress_message.delete()

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /settings command."""
    session = context.user_data.get('session', UserSession())
    
    settings_text = (
        "🔧 Current Settings:\n\n"
        f"Groq API Key: {'✅ Set' if session.groq_api_key else '❌ Not Set'}\n"
        f"Together API Key: {'✅ Set' if session.together_api_key else '❌ Not Set'}\n"
        f"Voice Response: {'✅ Enabled' if session.voice_response else '❌ Disabled'}\n"
        f"Selected Model: {session.selected_model}"
    )
    
    await update.message.reply_text(settings_text)

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /save command."""
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("No chat history to save.")
        return

    session = user_sessions[user_id]
    if not session.conversation_history:
        await update.message.reply_text("No chat history to save.")
        return

    try:
        # Save chat history
        filename = save_chat_history(
            messages=session.conversation_history,
            model_type="mistral-7b-instruct",
            export_format='json'  # You can make this configurable
        )
        await update.message.reply_text(f"Chat history saved to: {filename}")
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        await update.message.reply_text(f"Error saving chat history: {str(e)}")

async def temperature_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /temperature command."""
    if not context.args:
        await update.message.reply_text("Please provide a temperature value (0.0-1.0)")
        return

    try:
        temp = float(context.args[0])
        if not 0 <= temp <= 1:
            raise ValueError("Temperature must be between 0 and 1")

        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()

        session = user_sessions[user_id]
        session.temperature = temp
        await update.message.reply_text(f"Temperature set to: {temp}")
    except ValueError as e:
        await update.message.reply_text(str(e))

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /clear command."""
    if not update.message:
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("No chat history to clear.")
        return

    # Create inline keyboard for confirmation
    keyboard = [
        [
            InlineKeyboardButton("Yes, clear history", callback_data='clear_confirm'),
            InlineKeyboardButton("No, keep history", callback_data='clear_cancel')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚠️ Are you sure you want to clear your chat history?\n"
        "This action cannot be undone.",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()  # Answer the callback query to remove the loading state

    if query.data == 'clear_confirm':
        user_id = update.effective_user.id
        if user_id in user_sessions:
            user_sessions[user_id].conversation_history = []
            await query.edit_message_text("🗑️ Chat history cleared successfully!")
    elif query.data == 'clear_cancel':
        await query.edit_message_text("✅ Clear operation cancelled. Your chat history is preserved.")

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /export command."""
    if not update.message:
        return

    # Check if format is specified
    format_type = "markdown"  # default format
    if context.args:
        format_type = context.args[0].lower()
        if format_type not in ["markdown", "pdf"]:
            await update.message.reply_text(
                "❌ Invalid format. Please use:\n"
                "• `/export markdown` - Export as Markdown\n"
                "• `/export pdf` - Export as PDF",
                parse_mode='Markdown'
            )
            return

    user_id = update.effective_user.id
    if user_id not in user_sessions or not user_sessions[user_id].conversation_history:
        await update.message.reply_text("No chat history to export.")
        return

    # Send "processing" message
    processing_msg = await update.message.reply_text("📤 Processing your export request...")

    try:
        success, message, file_bytes = save_chat_history(
            user_sessions[user_id].conversation_history,
            format_type
        )

        if success and file_bytes:
            # Prepare the file
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            if format_type == "markdown":
                filename = f"chat_history_{current_time}.md"
                caption = "📝 Here's your chat history in Markdown format!"
            else:  # pdf
                filename = f"chat_history_{current_time}.pdf"
                caption = "📄 Here's your chat history in PDF format!"

            # Send the file
            await update.message.reply_document(
                document=BytesIO(file_bytes),
                filename=filename,
                caption=caption
            )
        else:
            await update.message.reply_text(f"❌ Export failed: {message}")

    except Exception as e:
        logger.error(f"Error in export_command: {str(e)}")
        await update.message.reply_text("❌ Sorry, something went wrong during export.")

    finally:
        # Delete the processing message
        await processing_msg.delete()

async def uploadenv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /uploadenv command."""
    await update.message.reply_text(
        "📤 Please upload a .env file containing your API keys.\n\n"
        "Format:\n"
        "```\n"
        "GROQ_API_KEY=your_groq_key\n"
        "TOGETHER_API_KEY=your_together_key\n"
        "```\n\n"
        "Make sure to send the file as a document.",
        parse_mode='Markdown'
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded documents."""
    session = context.user_data.get('session', UserSession())
    
    # Check if the file is a .env file
    if not update.message.document.file_name.endswith('.env'):
        await update.message.reply_text("❌ Please upload a .env file")
        return

    try:
        file = await context.bot.get_file(update.message.document.file_id)
        
        # Create a temporary file to store the downloaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            await file.download_to_memory(temp_file)
            temp_file_path = temp_file.name

        # Read and parse the .env file
        success_msg = []
        with open(temp_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'GROQ_API_KEY':
                            session.groq_api_key = value
                            success_msg.append("✅ Groq API key set successfully")
                        elif key == 'TOGETHER_API_KEY':
                            session.together_api_key = value
                            success_msg.append("✅ Together API key set successfully")
                    except ValueError:
                        continue

        # Clean up the temporary file
        os.unlink(temp_file_path)

        if success_msg:
            await update.message.reply_text("\n".join(success_msg))
        else:
            await update.message.reply_text(
                "❌ No valid API keys found in the file.\n"
                "Make sure your file contains GROQ_API_KEY and/or TOGETHER_API_KEY."
            )

        # Update the session in user_data
        context.user_data['session'] = session

    except Exception as e:
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    if update and isinstance(update, Update) and update.effective_message:
        text = "Sorry, an error occurred while processing your request."
        await update.effective_message.reply_text(text)

async def describe_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /describe command and direct photo messages for image analysis"""
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()
            
        session = user_sessions[user_id]
        
        if not session.groq_api_key:
            await update.message.reply_text(
                "Please set your Groq API key first using the /setgroqkey command"
            )
            return

        # Get the photo file
        if update.message.photo:
            photo = update.message.photo[-1]  # Get the largest size
        else:
            await update.message.reply_text("Please send an image to describe.")
            return

        # Download the photo
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()

        # Convert to base64
        photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')

        # Send typing action
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")

        # Create the client
        client = Groq(api_key=session.groq_api_key)

        # Create the message with the image - using correct format for vision model
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{photo_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "As a helpful assistant that describes images in detail, please describe this image. Focus on the main elements, colors, composition, and any notable features. Provide a clear and comprehensive description."
                    }
                ]
            }
        ]

        # Get the response
        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.2-11b-vision-preview",  # Using vision model
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        # Get the description
        description = response.choices[0].message.content

        # Send text response
        await update.message.reply_text(description)
        
        # Handle voice response
        try:
            # Send recording action
            await context.bot.send_chat_action(chat_id=update.message.chat_id, action="record_voice")
            status_message = await update.message.reply_text("🎙️ Converting description to speech...")
            
            # Create voice file
            voice_path = os.path.join(tempfile.gettempdir(), f'description_{user_id}.mp3')
            success = await text_to_speech_chunk(description, voice_path)
            
            if success and os.path.exists(voice_path):
                # Update status
                await status_message.edit_text("📤 Sending voice description...")
                
                # Send the voice message
                with open(voice_path, 'rb') as voice:
                    await update.message.reply_voice(
                        voice=voice,
                        caption="🎙️ Image Description"
                    )
                
                # Clean up
                os.remove(voice_path)
                await status_message.delete()
            else:
                await status_message.edit_text("❌ Could not generate voice description.")
                
        except Exception as voice_error:
            logger.error(f"Voice description error: {str(voice_error)}")
            await update.message.reply_text("Note: Voice description could not be generated.")

    except Exception as e:
        error_message = f"Error describing image: {str(e)}"
        logger.error(error_message)
        await update.message.reply_text(
            "Sorry, I encountered an error while describing the image. Please try again."
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent directly to the bot"""
    await describe_image(update, context)

# Supported audio formats
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.oga', '.opus', '.mp4', '.mpeg', '.mpga', '.webm'}

def get_file_extension(file_name: str) -> str:
    """Get the file extension from the file name."""
    return Path(file_name).suffix.lower()

def is_supported_format(file_name: str) -> bool:
    """Check if the file format is supported."""
    return get_file_extension(file_name) in SUPPORTED_FORMATS

def transcribe_audio(filename, prompt=None):
    """Transcribe English audio file using Groq API."""
    # Initialize the Groq client
    client = Groq()  # Make sure GROQ_API_KEY is set in your environment variables
    
    try:
        # Open the audio file
        with open(filename, "rb") as file:
            # Create a translation of the audio file
            translation = client.audio.translations.create(
                file=(filename, file.read()),  # Required audio file
                model="whisper-large-v3",  # Required model to use for translation
                prompt=prompt or "This is English audio, transcribe accurately",  # Set English context
                response_format="json",  # Optional
                temperature=0.0  # Optional
            )
            return translation.text
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise

async def transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /transcribe command for both YouTube videos and audio files."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a YouTube link or reply to an audio message to transcribe."
        )
        return

    url = context.args[0]
    if "youtube.com" in url or "youtu.be" in url:
        # Handle YouTube URL
        status_message = await update.message.reply_text("⏳ Downloading and processing YouTube video...")
        
        try:
            video_path, error = download_and_compress_video(url)
            if error:
                await status_message.edit_text(f"❌ Error: {error}")
                return
                
            await status_message.edit_text("🎵 Transcribing audio...")
            transcription = transcribe_audio(video_path)
            
            if transcription:
                # Send video file first
                with open(video_path, 'rb') as video_file:
                    await update.message.reply_video(
                        video=video_file,
                        caption="Downloaded video (will be saved until /clear is used)"
                    )
                # Then send transcription
                await status_message.edit_text(f"✅ Transcription:\n\n{transcription}")
            else:
                await status_message.edit_text("❌ Failed to transcribe the audio.")
        except Exception as e:
            await status_message.edit_text(f"❌ Error: {str(e)}")
    else:
        await update.message.reply_text("Please provide a valid YouTube link.")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio messages."""
    try:
        # Send initial processing message
        processing_msg = await update.message.reply_text(
            "🎵 Receiving your audio...\n⚠️ Note: Only English audio is supported",
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
            if transcription.startswith("⚠️ Sorry, this bot only transcribes English audio"):
                # If non-English audio was detected
                await processing_msg.edit_text(transcription)
            else:
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
                "❌ Sorry, I couldn't transcribe the audio. Please try again with clear English audio."
            )

        # Clean up the temporary file
        if file_path.exists():
            file_path.unlink()

    except Exception as e:
        logger.error(f"Error handling audio: {str(e)}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again with clear English audio."
        )

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

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show supported language information."""
    lang_text = (
        "🌐 *Supported Language for Audio Transcription*\n\n"
        "Currently, this bot only supports:\n"
        "• English (US)\n"
        "• English (UK)\n"
        "• English (International)\n\n"
        "⚠️ *Important Notes:*\n"
        "• Clear pronunciation helps accuracy\n"
        "• Minimal background noise preferred\n"
        "• Good audio quality recommended\n\n"
        "🎯 *Best Practices:*\n"
        "• Speak clearly and at normal speed\n"
        "• Avoid heavy accents if possible\n"
        "• Use good quality recording equipment\n"
        "• Record in a quiet environment\n\n"
        "Use /transcribe to start transcribing!"
    )
    await update.message.reply_text(lang_text)

async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show voice message instructions."""
    voice_text = (
        "🎤 *Voice Message Instructions*\n\n"
        "To send a voice message:\n"
        "1. Click the microphone icon (🎤)\n"
        "2. Hold to record your message\n"
        "3. Speak clearly in English\n"
        "4. Release to send\n\n"
        "⚠️ *Tips for Best Results:*\n"
        "• Find a quiet location\n"
        "• Speak at a normal pace\n"
        "• Hold phone close to mouth\n"
        "• Avoid background noise\n\n"
        "Maximum duration: 20 minutes"
    )
    await update.message.reply_text(voice_text)

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show audio file instructions."""
    audio_text = (
        "🎵 *Audio File Instructions*\n\n"
        "To send an audio file:\n"
        "1. Click the attachment icon (📎)\n"
        "2. Select 'Audio'\n"
        "3. Choose your English audio file\n"
        "4. Send the file\n\n"
        "📝 *Requirements:*\n"
        "• English audio only\n"
        "• Maximum size: 20MB\n"
        "• Supported formats: use /formats\n\n"
        "⚠️ *Tips:*\n"
        "• High-quality audio works best\n"
        "• Clear speech is important\n"
        "• Minimal background noise\n"
        "• Single speaker preferred"
    )
    await update.message.reply_text(audio_text)

async def text_to_speech_chunk(text: str, file_path: str, max_length: int = 500) -> bool:
    """Convert text to speech in smaller chunks for better performance."""
    try:
        # Split text into smaller chunks at sentence boundaries
        sentences = text.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > max_length:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_length = len(sentence)
            else:
                current_chunk.append(sentence)
                current_length += len(sentence)
        
        if current_chunk:
            chunks.append('. '.join(current_chunk))
        
        # Convert each chunk to speech
        for i, chunk in enumerate(chunks):
            tts = gTTS(text=chunk, lang='en', slow=False)
            chunk_path = f"{file_path}.part{i}"
            tts.save(chunk_path)
        
        # Combine all chunks (if multiple)
        if len(chunks) > 1:
            with open(file_path, 'wb') as outfile:
                for i in range(len(chunks)):
                    chunk_path = f"{file_path}.part{i}"
                    with open(chunk_path, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(chunk_path)
        else:
            # If only one chunk, just rename it
            os.rename(f"{file_path}.part0", file_path)
            
        return True
    except Exception as e:
        logger.error(f"Error in text_to_speech_chunk: {str(e)}")
        return False

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages and respond with both voice and text."""
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()
        
        session = user_sessions[user_id]
        
        # Get the message text
        message_text = update.message.text.strip()
        
        # Process the message and get response
        response = await process_message(message_text, session)
        
        # Send text response
        await update.message.reply_text(response)
        
        # Send voice response if enabled
        if session.voice_response:
            audio_file = await text_to_speech(response)
            if audio_file:
                await context.bot.send_voice(
                    chat_id=update.effective_chat.id,
                    voice=open(audio_file, 'rb')
                )
                os.remove(audio_file)  # Clean up the audio file
                
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def toggle_voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle voice responses on/off."""
    try:
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()
        
        session = user_sessions[user_id]
        session.voice_response = not session.voice_response
        
        status = "enabled ✅" if session.voice_response else "disabled ❌"
        await update.message.reply_text(
            f"Voice responses are now {status}",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in toggle_voice_command: {str(e)}")
        await update.message.reply_text("Sorry, I encountered an error while toggling voice responses.")

async def videos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all downloaded videos."""
    videos = get_downloaded_videos()
    if not videos:
        await update.message.reply_text("No videos have been downloaded yet.")
        return

    message = "📺 Downloaded Videos:\n\n"
    for video in videos:
        message += f"🎥 {video['name']}\n"
        message += f"📊 Size: {video['size']}\n\n"
    
    message += "\nUse /clear to delete all videos."
    await update.message.reply_text(message)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all downloaded videos."""
    result = clear_videos()
    await update.message.reply_text(result)

async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /maintenance command."""
    try:
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Please provide duration and message.\n"
                "Example: /maintenance 2h System upgrade in progress"
            )
            return

        duration_str = context.args[0].lower()
        message = " ".join(context.args[1:])

        # Parse duration (e.g., 2h, 30m)
        try:
            unit = duration_str[-1]
            value = int(duration_str[:-1])
            if unit == 'h':
                duration = timedelta(hours=value)
            elif unit == 'm':
                duration = timedelta(minutes=value)
            else:
                raise ValueError("Invalid duration unit")
        except ValueError:
            await update.message.reply_text(
                "Invalid duration format. Use format: 2h or 30m"
            )
            return

        # Set maintenance mode
        BOT_STATUS["is_maintenance"] = True
        BOT_STATUS["maintenance_message"] = message
        BOT_STATUS["maintenance_start"] = datetime.now()
        BOT_STATUS["maintenance_end"] = datetime.now() + duration

        # Notify all subscribed users
        notification = (
            "🔧 Bot Maintenance Notice\n\n"
            f"Message: {message}\n"
            f"Duration: {duration_str}\n"
            f"Start Time: {BOT_STATUS['maintenance_start'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Expected End: {BOT_STATUS['maintenance_end'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

        for subscribed_user in BOT_STATUS["notified_users"]:
            try:
                await context.bot.send_message(
                    chat_id=subscribed_user,
                    text=notification
                )
            except Exception as e:
                logger.error(f"Failed to notify user {subscribed_user}: {str(e)}")

        await update.message.reply_text("✅ Maintenance mode activated and users notified.")

        # Schedule maintenance end
        asyncio.create_task(end_maintenance(context.bot, duration))

    except Exception as e:
        await update.message.reply_text(f"Error setting maintenance mode: {str(e)}")

async def end_maintenance(bot, duration):
    """Automatically end maintenance after specified duration."""
    await asyncio.sleep(duration.total_seconds())
    if BOT_STATUS["is_maintenance"]:
        BOT_STATUS["is_maintenance"] = False
        # Notify all subscribed users
        for user_id in BOT_STATUS["notified_users"]:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text="✅ Maintenance completed! Bot is now back online."
                )
            except Exception as e:
                logger.error(f"Failed to notify user {user_id} about maintenance end: {str(e)}")

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /subscribe command."""
    try:
        user_id = update.effective_user.id
        if user_id not in BOT_STATUS["notified_users"]:
            BOT_STATUS["notified_users"].add(user_id)
            await update.message.reply_text(
                "✅ You have subscribed to bot status updates.\n"
                "You will be notified about maintenance and status changes."
            )
        else:
            await update.message.reply_text("You are already subscribed to status updates.")
    except Exception as e:
        await update.message.reply_text(f"Error subscribing: {str(e)}")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /unsubscribe command."""
    try:
        user_id = update.effective_user.id
        if user_id in BOT_STATUS["notified_users"]:
            BOT_STATUS["notified_users"].remove(user_id)
            await update.message.reply_text("✅ You have unsubscribed from bot status updates.")
        else:
            await update.message.reply_text("You are not subscribed to status updates.")
    except Exception as e:
        await update.message.reply_text(f"Error unsubscribing: {str(e)}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /status command."""
    try:
        if BOT_STATUS["is_maintenance"]:
            time_left = BOT_STATUS["maintenance_end"] - datetime.now()
            message = (
                "🔧 Bot is currently under maintenance\n\n"
                f"Message: {BOT_STATUS['maintenance_message']}\n"
                f"Started: {BOT_STATUS['maintenance_start'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Expected End: {BOT_STATUS['maintenance_end'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Time Remaining: {str(time_left).split('.')[0]}"
            )
        else:
            message = "✅ Bot is online and functioning normally."
        
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error checking status: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    if BOT_STATUS["is_maintenance"]:
        time_left = BOT_STATUS["maintenance_end"] - datetime.now()
        if time_left.total_seconds() > 0:
            await update.message.reply_text(
                "🔧 Bot is currently under maintenance\n\n"
                f"Message: {BOT_STATUS['maintenance_message']}\n"
                f"Expected to be back in: {str(time_left).split('.')[0]}"
            )
            return
        else:
            BOT_STATUS["is_maintenance"] = False

    # Continue with normal message handling
    await handle_text_message(update, context)

def setup_bot(token: str):
    """Initialize and configure the AIFusionBot"""
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setgroqkey", setgroqkey_command))
    application.add_handler(CommandHandler("settogetherkey", settogetherkey_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("imagine", imagine_command))
    application.add_handler(CommandHandler("enhance", enhance_command))
    application.add_handler(CommandHandler("describe", describe_image))
    application.add_handler(CommandHandler("transcribe", transcribe_command))
    application.add_handler(CommandHandler("formats", formats_command))
    application.add_handler(CommandHandler("voice", voice_command))
    application.add_handler(CommandHandler("audio", audio_command))
    application.add_handler(CommandHandler("togglevoice", toggle_voice_command))
    application.add_handler(CommandHandler("videos", videos_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("maintenance", maintenance_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, describe_image))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add error handler
    application.add_error_handler(error_handler)

    return application

def run_telegram_bot():
    """Main function to run the Telegram bot"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get bot token from environment
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Setup and run the bot
        app = setup_bot(token)
        logger.info("Starting bot in polling mode...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

if __name__ == "__main__":
    run_telegram_bot()