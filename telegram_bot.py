from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging
import os
import sys
import tempfile
import base64
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from io import BytesIO
import time
import json
from main import interactive_chat, save_chat_history, generate_image
from flask import Flask, request, jsonify
from groq import Groq
import asyncio
from gtts import gTTS
from youtube_utils import (
    download_and_compress_video,
    clear_videos,
    get_downloaded_videos,
    get_video_info
)
from tone_enhancer import ToneEnhancer

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

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
    "Basic Commands": {
        "/start": "Start the bot",
        "/help": "Show this help message",
        "/chat": "Chat with the bot",
        "/settings": "Show bot settings",
        "/status": "Check bot status"
    },
    "Media Commands": {
        "/imagine": "Generate images",
        "/enhance": "Enhance prompts",
        "/describe": "Describe images",
        "/audio_to_text": "Convert voice messages to text",
        "/videos": "List downloaded videos",
        "/clear": "Clear downloaded videos"
    },
    "API Commands": {
        "/setgroqkey": "Set your Groq API key",
        "/settogetherkey": "Set your Together AI key"
    },
    "Settings Commands": {
        "/togglevoice": "Toggle voice responses",
        "/subscribe": "Subscribe to bot status",
        "/unsubscribe": "Unsubscribe from bot status",
        "/clear_chat": "Clear chat history",
        "/maintenance": "Toggle maintenance mode (admin only)"
    }
}

# Group commands by category for help menu
COMMAND_CATEGORIES = {
    "🤖 Chat": ['chat'],
    "🎨 Image": ['imagine', 'enhance', 'describe'],
    "🔑 API Keys": ['setgroqkey', 'settogetherkey'],
    "🎵 Audio": ['audio_to_text', 'togglevoice'],
    "⚙️ Settings": ['settings', 'uploadenv', 'togglevoice'],
    "ℹ️ General": ['start', 'help'],
    "🔧 Maintenance": ['maintenance', 'status', 'subscribe', 'unsubscribe']
}

class UserSession:
    def __init__(self):
        self.conversation_history = []
        self.last_response = None
        self.last_image_prompt = None
        self.last_image_url = None
        self.selected_model = "mistral-7b-instruct"  # Default Groq model
        self.together_api_key = os.getenv('TOGETHER_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.last_enhanced_prompt = None
        self.voice_response = True
        self.subscribed_to_status = False  # New field for status subscription

BOT_STATUS = {
    "is_maintenance": False,
    "maintenance_message": "",
    "maintenance_start": None,
    "maintenance_end": None,
    "is_online": True,
    "last_offline_message": None,
    "notified_users": set(),
    "start_time": time.time(),  # Add this line to track bot start time
    "last_offline_time": None
}

subscribed_users = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "✨ *Welcome to AIFusionBot!* ✨\n\n"
        "🌟 Created By Amul Thantharate 🌟\n\n"
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
        "🔑 *Required API Keys*\n"
        "• Get Groq API key from: https://console.groq.com/keys\n"
        "• Get Together AI key from: https://www.together.ai\n"
        "• Use /setgroqkey and /settogetherkey to set them\n\n"
        "❓ Use /help to see all available commands!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_message = "🎯 *Available Commands*\n\n"
    
    # Organize commands by category
    categories = {
        "💬 Chat Commands": ['chat'],
        "🎨 Image Commands": ['imagine', 'enhance', 'describe'],
        "🎵 Audio Commands": ['transcribe', 'formats', 'voice', 'audio', 'lang'],
        "🔑 API Keys": ['setgroqkey', 'settogetherkey'],
        "⚙️ Settings": ['settings', 'uploadenv', 'togglevoice'],
        "ℹ️ General": ['start', 'help'],
        "🔧 Maintenance": ['maintenance', 'status', 'subscribe', 'unsubscribe'],
        "🌐 Translation": ['translate'],
        "📝 Text Processing": ['audio_to_text', 'clear_chat']
    }
    
    for category, cmd_list in categories.items():
        help_message += f"\n{category}:\n"
        for cmd in cmd_list:
            if cmd in COMMANDS:
                help_message += f"/{cmd} - {COMMANDS[cmd]}\n"
    
    help_message += "\n🔑 *API Keys Required*:\n"
    help_message += "• Groq API: https://console.groq.com/keys\n"
    help_message += "• Together AI: https://www.together.ai\n"
    
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def setopenaikey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This command is deprecated."""
    await update.message.reply_text(
        "⚠️ OpenAI integration has been removed from this bot. "
        "Please use Groq API instead with the /settogetherkey command."
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
        if not context.args:
            await update.message.reply_text(
                "Please provide a message after /chat\n"
                "Example: `/chat Hello, how are you?`",
                parse_mode='Markdown'
            )
            return
            
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()
            
        session = user_sessions[user_id]
        
        if not session.groq_api_key:
            await update.message.reply_text(
                "Please set your Groq API key in the .env file"
            )
            return
            
        # Get the message from arguments
        message = ' '.join(context.args)
        
        # Add user message to conversation history
        session.conversation_history.append({
            'role': 'user',
            'content': message
        })
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
        
        # Get AI response with proper API key
        response = interactive_chat(
            text=message,
            model_type="mistral-7b-instruct",
            api_key=session.groq_api_key
        )
        
        # Send text response
        await update.message.reply_text(response)
        
        # Add AI response to conversation history
        session.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Store the last response
        session.last_response = response

        # Handle voice response if enabled
        if session.voice_response:
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
        logger.error(f"Error in chat: {str(e)}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n"
            "Please try again later or contact support if the issue persists."
        )

async def imagine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /imagine command for image generation with prompt enhancement."""
    logger.info("Starting /imagine command...")
    
    if not update.message:
        logger.error("No message object found in update")
        return

    if not context.args:
        logger.info("No prompt provided with /imagine command")
        await update.message.reply_text(
            "Please provide a description after /imagine\n"
            "Example: `/imagine beautiful sunset over mountains, realistic, 4k, detailed`",
            parse_mode='Markdown'
        )
        return

    user_id = update.effective_user.id
    logger.info(f"Processing /imagine command for user {user_id}")
    
    if user_id not in user_sessions:
        logger.info(f"Creating new session for user {user_id}")
        user_sessions[user_id] = UserSession()

    session = user_sessions[user_id]
    if not session.together_api_key:
        logger.warning(f"Together API key not set for user {user_id}")
        await update.message.reply_text(
            "⚠️ Please set your Together API key first using:\n"
            "`/settogetherkey your_api_key`",
            parse_mode='Markdown'
        )
        return

    prompt = ' '.join(context.args)
    logger.info(f"Received prompt: {prompt}")

    # Send a message indicating that prompt enhancement has started
    progress_message = await update.message.reply_text(
        "🎨 Step 1/2: Enhancing your prompt... Please wait."
    )

    try:
        start_time = time.time()
        logger.info("Calling generate_image function...")
        # Pass the user_id to generate_image
        success, image_bytes, message, enhanced_prompt = generate_image(prompt, user_id=user_id)
        total_time = time.time() - start_time
        logger.info(f"Image generation completed in {total_time:.2f} seconds. Success: {success}")
        
        if success and image_bytes:
            logger.info("Image generated successfully, sending to user...")
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
            logger.error(f"Failed to generate image: {message}")
            await update.message.reply_text(f"❌ Failed to generate image: {message}")
    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}", exc_info=True)
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
    """Clear all downloaded files."""
    try:
        message = clear_videos()
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error clearing files: {str(e)}")
        await update.message.reply_text("Error clearing downloaded files.")

async def videos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all downloaded videos."""
    try:
        videos = get_downloaded_videos()
        if not videos:
            await update.message.reply_text("No videos have been downloaded yet.")
            return

        message = "📹 *Downloaded Videos:*\n"
        for video in videos:
            message += f"• {video['name']} ({video['size']})\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        await update.message.reply_text("Error listing downloaded videos.")

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
        logger.info("Starting image description process...")
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            logger.info(f"Creating new session for user {user_id}")
            user_sessions[user_id] = UserSession()
            
        session = user_sessions[user_id]
        
        if not session.groq_api_key:
            logger.warning(f"Groq API key not set for user {user_id}")
            await update.message.reply_text(
                "⚠️ Please set your Groq API key first using:\n"
                "`/setgroqkey your_api_key`",
                parse_mode='Markdown'
            )
            return

        # Get the photo file
        if update.message.photo:
            logger.info("Photo found in message")
            photo = update.message.photo[-1]  # Get the largest size
            logger.info(f"Photo size: {photo.width}x{photo.height}, file_id: {photo.file_id}")
        else:
            logger.warning("No photo found in message")
            await update.message.reply_text(
                "Please send a photo along with the /describe command, or just send a photo directly.",
                parse_mode='Markdown'
            )
            return

        # Download the photo
        try:
            logger.info("Downloading photo...")
            photo_file = await context.bot.get_file(photo.file_id)
            photo_bytes = await photo_file.download_as_bytearray()
            logger.info(f"Photo downloaded successfully, size: {len(photo_bytes)} bytes")
        except Exception as e:
            logger.error(f"Error downloading photo: {str(e)}", exc_info=True)
            await update.message.reply_text("Sorry, I couldn't download the photo. Please try again.")
            return

        # Convert to base64
        try:
            logger.info("Converting photo to base64...")
            photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
            logger.info("Photo converted to base64 successfully")
        except Exception as e:
            logger.error(f"Error converting photo to base64: {str(e)}", exc_info=True)
            await update.message.reply_text("Sorry, I couldn't process the photo. Please try again.")
            return

        # Send typing action
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")

        try:
            logger.info("Creating Groq client...")
            client = Groq(api_key=session.groq_api_key)
            logger.info("Groq client created successfully")

            # Create the message with the image
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

            logger.info("Making API request to Groq...")
            response = client.chat.completions.create(
                messages=messages,
                model="llama-3.2-11b-vision-preview",
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            logger.info("Received response from Groq")

            # Get the description
            description = response.choices[0].message.content
            logger.info("Description extracted from response")

            # Send text response
            await update.message.reply_text(description)
            logger.info("Text description sent to user")

        except Exception as e:
            error_message = f"Error with Groq API: {str(e)}"
            logger.error(error_message, exc_info=True)
            await update.message.reply_text(
                "Sorry, I encountered an error while analyzing the image. Please try again later."
            )
            return
            
        # Handle voice response if enabled
        if session.voice_response:
            try:
                logger.info("Starting voice response generation...")
                # Send recording action
                await context.bot.send_chat_action(chat_id=update.message.chat_id, action="record_voice")
                status_message = await update.message.reply_text("🎙️ Converting description to speech...")
                
                # Create voice file
                voice_path = os.path.join(tempfile.gettempdir(), f'description_{user_id}.mp3')
                success = await text_to_speech_chunk(description, voice_path)
                
                if success and os.path.exists(voice_path):
                    logger.info("Voice file created successfully")
                    # Update status
                    await status_message.edit_text("📤 Sending voice description...")
                    
                    # Send the voice message
                    with open(voice_path, 'rb') as voice:
                        await update.message.reply_voice(
                            voice=voice,
                            caption="🎙️ Image Description"
                        )
                    logger.info("Voice message sent successfully")
                    
                    # Clean up
                    os.remove(voice_path)
                    await status_message.delete()
                else:
                    logger.error("Failed to create voice file")
                    await status_message.edit_text("❌ Could not generate voice description.")
                    
            except Exception as voice_error:
                logger.error(f"Voice description error: {str(voice_error)}", exc_info=True)
                await update.message.reply_text("Note: Voice description could not be generated.")

    except Exception as e:
        error_message = f"Error describing image: {str(e)}"
        logger.error(error_message, exc_info=True)
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
            file_name = update.message.audio.file_name
            if not is_supported_format(file_name):
                await processing_msg.edit_text(
                    f"❌ Sorry, the format {get_file_extension(file_name)} is not supported.\n"
                    "Use /formats to see supported formats."
                )
                return
            file = await update.message.audio.get_file()
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
    """Deprecated: This command has been removed."""
    await update.message.reply_text(
        "⚠️ The /audio command has been removed. Please use /audio_to_text to transcribe voice messages."
    )

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

async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /maintenance command."""
    try:
        # Check if user is admin (you can modify this check as needed)
        user_id = update.effective_user.id
        if user_id not in user_sessions or not user_sessions[user_id].groq_api_key:
            await update.message.reply_text(
                "⚠️ You need to be registered with an API key to use maintenance mode.\n"
                "Use /setgroqkey to set your API key first."
            )
            return

        # Parse command arguments
        args = context.args if context.args else []
        
        # If no arguments, show current status
        if not args:
            status = "🔧 ON" if BOT_STATUS["is_maintenance"] else "✅ OFF"
            message = BOT_STATUS["maintenance_message"] or "No message set"
            end_time = BOT_STATUS["maintenance_end"]
            
            if end_time:
                time_left = end_time - datetime.now()
                if time_left.total_seconds() > 0:
                    time_str = str(time_left).split('.')[0]
                else:
                    time_str = "Expired"
            else:
                time_str = "No duration set"
            
            await update.message.reply_text(
                f"Maintenance Mode: {status}\n"
                f"Message: {message}\n"
                f"Time Remaining: {time_str}"
            )
            return

        # Parse maintenance command
        if args[0].lower() in ['on', 'true', '1']:
            # Get duration (in minutes) and message
            duration = 30  # Default 30 minutes
            message = "Scheduled maintenance"
            
            if len(args) > 1:
                try:
                    duration = int(args[1])
                except ValueError:
                    await update.message.reply_text("Duration must be a number in minutes. Using default 30 minutes.")
            
            if len(args) > 2:
                message = ' '.join(args[2:])

            # Set maintenance mode
            BOT_STATUS["is_maintenance"] = True
            BOT_STATUS["maintenance_message"] = message
            BOT_STATUS["maintenance_start"] = datetime.now()
            BOT_STATUS["maintenance_end"] = datetime.now() + timedelta(minutes=duration)

            # Schedule end of maintenance
            asyncio.create_task(end_maintenance(context.bot, duration))

            # Notify all users
            notification = (
                "🔧 Bot entering maintenance mode\n\n"
                f"Message: {message}\n"
                f"Duration: {duration} minutes"
            )
            await notify_subscribers(context.application, notification)

            await update.message.reply_text(
                f"✅ Maintenance mode activated for {duration} minutes\n"
                f"Message: {message}"
            )

        elif args[0].lower() in ['off', 'false', '0']:
            # Turn off maintenance mode
            BOT_STATUS["is_maintenance"] = False
            BOT_STATUS["maintenance_message"] = ""
            BOT_STATUS["maintenance_start"] = None
            BOT_STATUS["maintenance_end"] = None

            # Notify all users
            notification = "✅ Maintenance mode ended"
            await notify_subscribers(context.application, notification)

            await update.message.reply_text("✅ Maintenance mode deactivated")

        else:
            await update.message.reply_text(
                "Invalid command. Use:\n"
                "/maintenance on [duration] [message] - Turn on maintenance mode\n"
                "/maintenance off - Turn off maintenance mode\n"
                "/maintenance - Show current status"
            )

    except Exception as e:
        logger.error(f"Error in maintenance command: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Sorry, I encountered an error while processing the maintenance command."
        )

async def end_maintenance(bot, duration):
    """Automatically end maintenance after specified duration."""
    try:
        await asyncio.sleep(duration * 60)  # Convert minutes to seconds
        if BOT_STATUS["is_maintenance"]:
            BOT_STATUS["is_maintenance"] = False
            BOT_STATUS["maintenance_message"] = ""
            BOT_STATUS["maintenance_start"] = None
            BOT_STATUS["maintenance_end"] = None

            # Notify all users
            notification = "✅ Scheduled maintenance completed"
            for user_id in get_subscribers():
                try:
                    await bot.send_message(chat_id=user_id, text=notification)
                except Exception as e:
                    logger.error(f"Failed to notify user {user_id}: {str(e)}")

    except Exception as e:
        logger.error(f"Error ending maintenance: {str(e)}", exc_info=True)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe to bot status notifications."""
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    
    user_sessions[user_id].subscribed_to_status = True
    subscribed_users[user_id] = update.effective_chat.id
    
    await update.message.reply_text(
        "✅ You are now subscribed to bot status notifications.\n"
        "You will receive alerts when the bot goes offline or comes back online."
    )

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe from bot status notifications."""
    user_id = update.effective_user.id
    if user_id in user_sessions:
        user_sessions[user_id].subscribed_to_status = False
    if user_id in subscribed_users:
        del subscribed_users[user_id]
    
    await update.message.reply_text(
        "❌ You are now unsubscribed from bot status notifications."
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if the bot is online."""
    try:
        # Get bot information to verify connection
        bot_info = await context.bot.get_me()
        current_time = time.time()
        start_time = BOT_STATUS.get("start_time", current_time)
        uptime = current_time - start_time
        
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        status_message = (
            "🟢 Bot Status: Online\n"
            f"Bot Name: {bot_info.first_name}\n"
            f"Username: @{bot_info.username}\n"
            f"Uptime: {hours}h {minutes}m\n"
            f"Maintenance Mode: {'🔧 Yes' if BOT_STATUS['is_maintenance'] else '✅ No'}"
        )
        await update.message.reply_text(status_message)
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        await update.message.reply_text("🔴 Bot Status: Error checking status")

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

async def notify_subscribers(application: Application, message: str):
    """Send notification to all subscribed users."""
    for chat_id in subscribed_users.values():
        try:
            await application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send notification to {chat_id}: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors and notify subscribers."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    error_message = (
        "🔴 *Bot Status Alert*\n\n"
        "The bot is currently experiencing technical difficulties.\n"
        "Our team has been notified and is working on the issue.\n\n"
        f"Error: `{str(context.error)}`"
    )
    
    await notify_subscribers(context.application, error_message)

async def on_startup(application: Application):
    """Notify subscribers when bot starts up."""
    startup_message = (
        "🟢 *Bot Status Alert*\n\n"
        "The bot is now online and ready to use!\n"
        "All systems are operational."
    )
    await notify_subscribers(application, startup_message)

async def audio_to_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert voice messages to text using Groq."""
    try:
        # Check if there's a voice message
        voice = update.message.voice or update.message.audio
        if not voice:
            await update.message.reply_text(
                "Please send a voice message or audio file to transcribe.",
                parse_mode='Markdown'
            )
            return

        # Get user session
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()
        session = user_sessions[user_id]

        if not session.groq_api_key:
            await update.message.reply_text(
                "⚠️ Please set your Groq API key first using:\n"
                "`/setgroqkey your_api_key`",
                parse_mode='Markdown'
            )
            return

        # Send typing action
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
        status_message = await update.message.reply_text("🎧 Processing audio...")

        # Download the voice message
        voice_file = await context.bot.get_file(voice.file_id)
        voice_bytes = await voice_file.download_as_bytearray()

        # Save to temporary file
        temp_path = os.path.join(tempfile.gettempdir(), f'voice_{user_id}.ogg')
        with open(temp_path, 'wb') as f:
            f.write(voice_bytes)

        # Convert audio to base64
        with open(temp_path, 'rb') as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

        # Create Groq client
        client = Groq(api_key=session.groq_api_key)

        # Create the transcription prompt
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that transcribes audio. Please transcribe the following audio file accurately."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "audio",
                        "audio_url": {
                            "url": f"data:audio/ogg;base64,{audio_base64}"
                        }
                    }
                ]
            }
        ]

        # Get transcription
        response = client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        transcript = response.choices[0].message.content.strip()
        
        # Send transcription
        await status_message.edit_text(
            f"📝 Transcription:\n\n{transcript}",
            parse_mode='Markdown'
        )

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

    except Exception as e:
        logger.error(f"Audio processing error: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Sorry, I encountered an error while processing the audio. Please try again."
        )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear the chat history for the current user."""
    try:
        user_id = update.effective_user.id
        if user_id in user_sessions:
            user_sessions[user_id].conversation_history = []
            await update.message.reply_text(
                "🧹 Chat history cleared successfully!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "No chat history found to clear.",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Clear chat error: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Sorry, I encountered an error while clearing the chat history. Please try again."
        )

def setup_bot(token: str) -> Application:
    """Set up and configure the bot with all handlers."""
    # Create application
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("togglevoice", toggle_voice_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("imagine", imagine_command))
    application.add_handler(CommandHandler("enhance", enhance_command))
    application.add_handler(CommandHandler("describe", describe_image))
    application.add_handler(CommandHandler("audio_to_text", audio_to_text))
    application.add_handler(CommandHandler("clear_chat", clear_chat))
    application.add_handler(CommandHandler("maintenance", maintenance_command))
    application.add_handler(CommandHandler("videos", videos_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    return application

def run_bot():
    """Run the bot."""
    try:
        # Initialize bot status
        BOT_STATUS["start_time"] = time.time()
        
        # Create and run application
        application = setup_bot(TELEGRAM_BOT_TOKEN)
        
        # Run the bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        raise

if __name__ == "__main__":
    run_bot()