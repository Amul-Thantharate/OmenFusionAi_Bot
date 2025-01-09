from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from datetime import datetime, timedelta
import os
import time
import logging
import tempfile
from pathlib import Path
import base64
from groq import Groq
import asyncio
from gtts import gTTS
import html
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv
import video_insights
from constants import HELP_MESSAGE, SUMMARY_PROMPT, MEDIA_FOLDER
from image_generator import AIImageGenerator
from image_caption import ImageCaptioner
from video_insights import get_insights

# Initialize image generator and captioner
image_generator = AIImageGenerator()
image_captioner = ImageCaptioner()

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
if not ROOT_PASSWORD:
    raise ValueError("ROOT_PASSWORD not found in environment variables")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create temp directory for files
TEMP_DIR = Path(tempfile.gettempdir()) / "aifusionbot_temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Global variable for user sessions
user_sessions = {}

# Dictionary of available commands and their descriptions
COMMANDS = {
    "/start": "Start the bot",
    "/help": "Show help message",
    "/chat": "Start a chat conversation",
    "/settings": "Configure bot settings",
    "/togglevoice": "Toggle voice responses",
    "/imagine": "Generate an image from text using Replicate",
    "/caption": "Generate a detailed caption for an image",
    "/enhance": "Enhance your text",
    "/describe": "Analyze an image",
    "/clear_chat": "Clear chat history",
    "/export": "Export chat history",
    "/analyze_video": "Analyze a video file",
    "/status": "Check bot status",
    "/subscribe": "Subscribe to bot updates",
    "/unsubscribe": "Unsubscribe from updates",
    "/maintenance": "Toggle maintenance mode (Admin only)",
    "/setup_commands": "Update bot commands (Admin only)"
}

# Group commands by category for help menu
COMMAND_CATEGORIES = {
    "🤖 Chat": ['chat', 'clear_chat', 'export'],
    "🎨 Media": ['imagine', 'caption', 'enhance', 'describe', 'analyze_video'],
    "🔊 Settings": ['settings', 'togglevoice'],
    "📊 Status": ['status', 'subscribe', 'unsubscribe'],
    "ℹ️ General": ['start', 'help'],
    "🔐 Admin": ['maintenance', 'setup_commands']
}

class UserSession:
    def __init__(self):
        self.conversation_history = []
        self.last_response = None
        self.last_image_prompt = None
        self.last_image_url = None
        self.last_photo = None  # Store last photo for inline keyboard actions
        self.selected_model = "llama3-70b-8192"  # Default Groq model
        self.replicate_api_key = os.getenv('REPLICATE_API_KEY')
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
    if not update.message:
        return

    welcome_message = (
        "🤖 Welcome to AIFusionBot!\n\n"
        "🤖 Cereate by Amul Thantharate\n\n"
        "I'm your AI assistant that can help you with various tasks:\n\n"
        "🗣️ Chat - Have natural conversations with AI\n"
        "🎨 Images - Generate and analyze images\n"
        "🎥 Video - Analyze video content\n"
        "📝 Text - Enhance and improve your text\n"
        "🔊 Voice - Toggle voice responses\n"
        "📊 Status - Get bot updates and notifications\n\n"
        "Type /help to see all available commands!"
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    if not update.message:
        return
        
    help_text = "🤖 *AIFusionBot Commands*\n\n"
    
    # Add regular categories first
    for category, commands in COMMAND_CATEGORIES.items():
        if category != "🔐 Admin":  # Skip admin commands for now
            help_text += f"\n{category}\n"
            for cmd in commands:
                cmd_with_slash = f"/{cmd}"
                if cmd_with_slash in COMMANDS:
                    description = COMMANDS[cmd_with_slash].replace("_", "\\_")  # Escape underscores
                    help_text += f"• `{cmd_with_slash}` \\- {description}\n"
    
    # Add admin commands separately
    if "🔐 Admin" in COMMAND_CATEGORIES:
        help_text += "\n🔐 *Admin Commands*\n"
        for cmd in COMMAND_CATEGORIES["🔐 Admin"]:
            cmd_with_slash = f"/{cmd}"
            if cmd_with_slash in COMMANDS:
                description = COMMANDS[cmd_with_slash].replace("_", "\\_")  # Escape underscores
                help_text += f"• `{cmd_with_slash}` \\- {description}\n"
    
    help_text += "\n_For more information about what I can do, type_ `/start`"
    
    try:
        await update.message.reply_text(
            help_text,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        # Fallback to plain text if Markdown fails
        plain_text = help_text.replace('*', '').replace('_', '').replace('`', '')
        await update.message.reply_text(plain_text)
        logging.error(f"Error sending help message with Markdown: {str(e)}")

async def setopenaikey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This command is deprecated."""
    await update.message.reply_text(
        " OpenAI integration has been removed from this bot. "
        "Please use Groq API instead with the /settogetherkey command."
    )

async def settogetherkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This command is deprecated."""
    await update.message.reply_text(
        "Together AI integration has been replaced with Replicate. "
        "Please set your Replicate API key in the .env file."
    )

async def interactive_chat(text: str, model_type: str, api_key: str) -> str:
    """Handle chat interaction with Groq API."""
    try:
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Create chat completion (not async)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ],
            model=model_type,
            temperature=0.7,
            max_tokens=1000,
        )
        
        # Return the response text
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error in interactive_chat: {e}")
        raise Exception(f"Failed to get response from Groq API: {str(e)}")

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
        response = await interactive_chat(
            text=message,
            model_type="llama3-70b-8192",
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
                status_message = await update.message.reply_text(" Converting text to speech...")
                
                # Create voice file
                voice_path = os.path.join(tempfile.gettempdir(), f'response_{user_id}.mp3')
                success = await text_to_speech_chunk(response, voice_path)
                
                if success and os.path.exists(voice_path):
                    # Update status
                    await status_message.edit_text(" Sending voice message...")
                    
                    # Send the voice message
                    with open(voice_path, 'rb') as voice:
                        await update.message.reply_voice(
                            voice=voice,
                            caption=" Voice Message"
                        )
                    
                    # Clean up
                    os.remove(voice_path)
                    await status_message.delete()
                else:
                    await status_message.edit_text(" Could not generate voice message.")
                
            except Exception as voice_error:
                logger.error(f"Voice message error: {str(voice_error)}")
                await update.message.reply_text("Note: Voice message could not be generated.")
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        await update.message.reply_text(
            f" Error: {str(e)}\n"
            "Please try again later or contact support if the issue persists."
        )

async def imagine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /imagine command for image generation with prompt enhancement."""
    if not update.message:
        return

    # Check if there's a prompt
    if not context.args:
        await update.message.reply_text(
            "Please provide a prompt for the image generation.\n"
            "Example: `/imagine a beautiful sunset over mountains`",
            parse_mode='Markdown'
        )
        return

    prompt = ' '.join(context.args)

    # Send initial status
    status_message = await update.message.reply_text(
        "🎨 Step 1/2: Enhancing your prompt..."
    )

    try:
        # Enhance the prompt
        enhanced_prompt = image_generator.enhance_prompt(prompt)
        if not enhanced_prompt:
            await status_message.edit_text("❌ Failed to enhance the prompt. Please try again.")
            return

        # Update status message
        await status_message.edit_text("🎨 Step 2/2: Generating image from enhanced prompt...")

        # Generate the image
        start_time = time.time()
        success, image_data, error_message = image_generator.generate_image(enhanced_prompt)
        total_time = time.time() - start_time

        if success and image_data:
            # Convert base64 to bytes
            image_bytes = base64.b64decode(image_data)
            
            # Create BytesIO object
            image_io = io.BytesIO(image_bytes)
            image_io.name = 'generated_image.png'

            # Send the image first
            await update.message.reply_photo(
                photo=image_io,
                caption=f"⏱️ Generated in {total_time:.1f}s",
                parse_mode='Markdown'
            )

            # Send prompts as a separate message
            prompts_message = (
                f"🎨 *Original prompt:*\n`{prompt}`\n\n"
                f"✨ *Enhanced prompt:*\n`{enhanced_prompt}`"
            )
            await update.message.reply_text(prompts_message, parse_mode='Markdown')
            await status_message.delete()
        else:
            error_msg = f"Failed to generate image: {error_message}"
            logger.error(error_msg)
            await status_message.edit_text(f"❌ {error_msg}")

    except Exception as e:
        error_msg = f"Error during image generation: {str(e)}"
        logger.error(error_msg)
        await status_message.edit_text(f"❌ {error_msg}")

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
    if not session.replicate_api_key:
        await update.message.reply_text(
            " Please set your Replicate API key first using:\n"
            "`/setreplicatekey your_api_key`",
            parse_mode='Markdown'
        )
        return

    text = ' '.join(context.args)

    # Send a message indicating that enhancement has started
    progress_message = await update.message.reply_text(
        " Enhancing your text... Please wait."
    )

    try:
        from tone_enhancer import ToneEnhancer
        enhancer = ToneEnhancer()
        
        # Set the API key from session
        enhancer.replicate_api_key = session.replicate_api_key
        
        start_time = time.time()
        success, enhanced_text, error = await enhancer.enhance_text(text)
        total_time = time.time() - start_time
        
        if success and enhanced_text:
            response = (
                f" Original text:\n`{text}`\n\n"
                f" Enhanced version:\n`{enhanced_text}`\n\n"
                f" Enhanced in {total_time:.2f} seconds"
            )
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            error_msg = f" Failed to enhance text: {error}"
            logger.error(error_msg)
            await update.message.reply_text(error_msg)
    except Exception as e:
        error_msg = f"Error in text enhancement: {str(e)}"
        logger.error(error_msg)
        await update.message.reply_text(
            " Sorry, something went wrong while enhancing the text. Please try again later."
        )
    finally:
        # Delete the progress message
        await progress_message.delete()

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /settings command."""
    session = context.user_data.get('session', UserSession())
    
    settings_text = (
        " Current Settings:\n\n"
        f"Groq API Key: {' Set' if session.groq_api_key else ' Not Set'}\n"
        f"Replicate API Key: {' Set' if session.replicate_api_key else ' Not Set'}\n"
        f"Voice Response: {' Enabled' if session.voice_response else ' Disabled'}\n"
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

async def describe_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /describe command and direct photo messages for image analysis"""
    try:
        # Get the photo file
        if update.message.photo:
            photo = update.message.photo[-1]  # Get the largest size
        else:
            await update.message.reply_text("Please send a photo to describe or use this command as a reply to a photo.")
            return

        # Get user session
        user_id = update.effective_user.id
        if user_id not in user_sessions:
            user_sessions[user_id] = UserSession()
        session = user_sessions[user_id]

        # Check if Groq API key is set
        if not session.groq_api_key:
            await update.message.reply_text(
                "Please set your Groq API key first using /setgroqkey command."
            )
            return

        await update.message.reply_text("Analyzing the image... 🔍")

        # Get the file URL
        photo_file = await context.bot.get_file(photo.file_id)
        file_url = photo_file.file_path

        # Create Groq client
        client = Groq(api_key=session.groq_api_key)
        logging.info("Groq client created successfully")

        # Prepare the message for image analysis
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please describe this image in detail. Focus on the main elements, colors, composition, and any notable features."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": file_url
                        }
                    }
                ]
            }
        ]

        logging.info("Making API request to Groq...")
        
        # Make the API request
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        logging.info("Received response from Groq")

        # Extract the description
        description = response.choices[0].message.content
        logging.info("Description extracted from response")

        # Send the text description
        await update.message.reply_text(description)
        logging.info("Text description sent to user")

        # Generate and send voice response if enabled
        if session.voice_response:
            logging.info("Starting voice response generation...")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_voice")
            
            # Create voice file path
            voice_path = os.path.join(TEMP_DIR, f"description_{photo.file_id}.mp3")
            
            # Convert text to speech
            success = await text_to_speech_chunk(description, voice_path)
            
            if success:
                # Send voice message
                with open(voice_path, 'rb') as voice_file:
                    await context.bot.send_voice(
                        chat_id=update.effective_chat.id,
                        voice=voice_file,
                        caption="🎧 Voice description"
                    )
                # Clean up voice file
                os.remove(voice_path)
            else:
                await update.message.reply_text("Sorry, I couldn't generate the voice description.")
                logging.error("Failed to generate voice description")

    except Exception as e:
        logging.error(f"Error in image description: {str(e)}")
        await update.message.reply_text(
            "Sorry, I encountered an error while processing your image. Please try again later."
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent directly to the bot"""
    await handle_photo(update, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent directly to the bot with analysis options."""
    if not update.message or not update.message.photo:
        return

    # Create inline keyboard with options
    keyboard = [
        [
            InlineKeyboardButton("📝 Describe Image", callback_data=f"describe_{update.message.message_id}"),
            InlineKeyboardButton("🔍 Generate Caption", callback_data=f"caption_{update.message.message_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Store the photo information in user session
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    
    session = user_sessions[user_id]
    session.last_photo = update.message.photo[-1]  # Store the largest photo

    await update.message.reply_text(
        "What would you like to do with this image?",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks from inline keyboard."""
    query = update.callback_query
    await query.answer()

    if not query.data:
        return

    action, message_id = query.data.split('_')
    user_id = query.from_user.id

    if user_id not in user_sessions:
        await query.edit_message_text("Session expired. Please send the image again.")
        return

    session = user_sessions[user_id]
    if not hasattr(session, 'last_photo'):
        await query.edit_message_text("Image not found. Please send the image again.")
        return

    try:
        photo_file = await context.bot.get_file(session.last_photo.file_id)
        photo_url = photo_file.file_path
        
        if action == "describe":
            # Create a mock update object to reuse describe_image
            mock_message = type('MockMessage', (), {
                'photo': [session.last_photo],
                'reply_text': query.edit_message_text,
                'effective_chat': query.message.chat
            })
            mock_update = type('MockUpdate', (), {
                'message': mock_message,
                'effective_user': query.from_user,
                'effective_chat': query.message.chat
            })
            
            # Call the existing describe_image function
            await describe_image(mock_update, context)

        elif action == "caption":
            await query.edit_message_text("🤔 Generating creative caption...")
            success, caption = await image_captioner.generate_caption(
                photo_url, 
                "Generate a creative and engaging caption for this image."
            )
            
            if success:
                await query.edit_message_text(f"🎨 Creative Caption:\n\n{caption}")
            else:
                await query.edit_message_text(f"❌ Error: {caption}")

    except Exception as e:
        logger.error(f"Error in button callback: {str(e)}")
        await query.edit_message_text("❌ Sorry, something went wrong. Please try again later.")

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
        
        status = "enabled " if session.voice_response else "disabled "
        await update.message.reply_text(
            f"Voice responses are now {status}",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in toggle_voice_command: {str(e)}")
        await update.message.reply_text("Sorry, I encountered an error while toggling voice responses.")

async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /maintenance command. Requires root password."""
    
    # Check if password is provided
    if not context.args:
        await update.message.reply_text(
            " Admin authentication required.\n\n"
            "Usage: `/maintenance <password> [on/off] [duration] [message]`\n"
            "Example: `/maintenance yourpassword on 30 System upgrade`",
            parse_mode='Markdown'
        )
        return
    
    # Verify password
    provided_password = context.args[0]
    if provided_password != ROOT_PASSWORD:
        await update.message.reply_text(" Invalid admin password.")
        return
    
    # Remove password from args before processing command
    context.args = context.args[1:]
    
    # If no further arguments, show current status
    if not context.args:
        status = " ON" if BOT_STATUS["is_maintenance"] else " OFF"
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
    if context.args[0].lower() in ['on', 'true', '1']:
        # Get duration (in minutes) and message
        duration = 30  # Default 30 minutes
        message = "Scheduled maintenance"
        
        if len(context.args) > 1:
            try:
                duration = int(context.args[1])
            except ValueError:
                await update.message.reply_text("Duration must be a number in minutes. Using default 30 minutes.")
        
        if len(context.args) > 2:
            message = ' '.join(context.args[2:])

        # Set maintenance mode
        BOT_STATUS["is_maintenance"] = True
        BOT_STATUS["maintenance_message"] = message
        BOT_STATUS["maintenance_start"] = datetime.now()
        BOT_STATUS["maintenance_end"] = datetime.now() + timedelta(minutes=duration)

        # Schedule end of maintenance
        asyncio.create_task(end_maintenance(context.bot, duration))

        # Notify all users
        notification = (
            " Bot entering maintenance mode\n\n"
            f"Message: {message}\n"
            f"Duration: {duration} minutes"
        )
        await notify_subscribers(context.application, notification)

        await update.message.reply_text(
            f" Maintenance mode activated for {duration} minutes\n"
            f"Message: {message}"
        )

    elif context.args[0].lower() in ['off', 'false', '0']:
        # Turn off maintenance mode
        BOT_STATUS["is_maintenance"] = False
        BOT_STATUS["maintenance_message"] = ""
        BOT_STATUS["maintenance_start"] = None
        BOT_STATUS["maintenance_end"] = None

        # Notify all users
        notification = " Maintenance mode ended"
        await notify_subscribers(context.application, notification)

        await update.message.reply_text(" Maintenance mode deactivated")

    else:
        await update.message.reply_text(
            "Invalid command. Use:\n"
            "/maintenance <password> on [duration] [message] - Turn on maintenance mode\n"
            "/maintenance <password> off - Turn off maintenance mode\n"
            "/maintenance <password> - Show current status"
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
            notification = " Scheduled maintenance completed"
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
        " You are now subscribed to bot status notifications.\n"
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
        " You are now unsubscribed from bot status notifications."
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
            " Bot Status: Online\n"
            f"Bot Name: {bot_info.first_name}\n"
            f"Username: @{bot_info.username}\n"
            f"Uptime: {hours}h {minutes}m\n"
            f"Maintenance Mode: {' Yes' if BOT_STATUS['is_maintenance'] else ' No'}"
        )
        await update.message.reply_text(status_message)
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        await update.message.reply_text(" Bot Status: Error checking status")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    if BOT_STATUS["is_maintenance"]:
        time_left = BOT_STATUS["maintenance_end"] - datetime.now()
        if time_left.total_seconds() > 0:
            await update.message.reply_text(
                " Bot is currently under maintenance\n\n"
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
        " *Bot Status Alert*\n\n"
        "The bot is currently experiencing technical difficulties.\n"
        "Our team has been notified and is working on the issue.\n\n"
        f"Error: `{str(context.error)}`"
    )
    
    await notify_subscribers(context.application, error_message)

async def on_startup(application: Application):
    """Notify subscribers when bot starts up."""
    startup_message = (
        " *Bot Status Alert*\n\n"
        "The bot is now online and ready to use!\n"
        "All systems are operational."
    )
    await notify_subscribers(application, startup_message)

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear the chat history for the current user."""
    try:
        user_id = update.effective_user.id
        if user_id in user_sessions:
            user_sessions[user_id].conversation_history = []
            await update.message.reply_text(
                " Chat history cleared successfully!",
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

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export chat history and images in Markdown and HTML formats."""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if user_id not in user_sessions:
            await update.message.reply_text(" No chat history found to export.")
            return
        
        # Create export directory if it doesn't exist
        export_dir = Path(f"exports/user_{user_id}")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get chat history from user session
        session = user_sessions[user_id]
        chat_history = session.conversation_history if hasattr(session, 'conversation_history') else []
        
        if not chat_history:
            await update.message.reply_text(" No messages to export.")
            return
        
        # Export as Markdown
        md_file = export_dir / f"chat_export_{timestamp}.md"
        html_file = export_dir / f"chat_export_{timestamp}.html"
        
        # Create Markdown export
        with md_file.open('w', encoding='utf-8') as f:
            f.write("# Chat History Export\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for msg in chat_history:
                # Handle different message formats
                if isinstance(msg, dict):
                    role = " Bot" if msg.get('role') == 'assistant' else " You"
                    content = msg.get('content', '')
                else:
                    # If message is not a dict, try to convert it to string
                    role = " Message"
                    content = str(msg)
                
                f.write(f"## {role}\n\n{content}\n\n")
                
                # Handle images if present
                if isinstance(msg, dict) and 'image_url' in msg:
                    f.write(f"![Image]({msg['image_url']})\n\n")
        
        # Create HTML export
        with html_file.open('w', encoding='utf-8') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chat History Export</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .message { margin: 20px 0; padding: 15px; border-radius: 10px; }
        .bot { background-color: #f0f0f0; }
        .user { background-color: #e3f2fd; }
        .default { background-color: #fff3e0; }
        .timestamp { color: #666; font-size: 0.8em; }
        img { max-width: 100%; height: auto; border-radius: 5px; margin: 10px 0; }
        h1 { color: #2196F3; }
    </style>
</head>
<body>
            """)
            
            f.write(f"<h1>Chat History Export</h1>")
            f.write(f"<p class='timestamp'>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
            
            for msg in chat_history:
                if isinstance(msg, dict):
                    role = " Bot" if msg.get('role') == 'assistant' else " You"
                    content = html.escape(msg.get('content', '')).replace('\n', '<br>')
                    msg_class = 'bot' if msg.get('role') == 'assistant' else 'user'
                else:
                    role = " Message"
                    content = html.escape(str(msg)).replace('\n', '<br>')
                    msg_class = 'default'
                
                f.write(f"<div class='message {msg_class}'>")
                f.write(f"<strong>{role}</strong><br>")
                f.write(f"{content}")
                
                # Handle images
                if isinstance(msg, dict) and 'image_url' in msg:
                    f.write(f"<br><img src='{html.escape(msg['image_url'])}' alt='Generated Image'>")
                
                f.write("</div>")
            
            f.write("""
</body>
</html>
            """)
        
        # Send the exported files
        await update.message.reply_text(
            " Export completed! Here are your files:",
            parse_mode='Markdown'
        )
        
        # Send Markdown file
        await context.bot.send_document(
            chat_id=chat_id,
            document=md_file.open('rb'),
            filename=md_file.name,
            caption=" Markdown Export"
        )
        
        # Send HTML file
        await context.bot.send_document(
            chat_id=chat_id,
            document=html_file.open('rb'),
            filename=html_file.name,
            caption=" HTML Export"
        )
        
    except Exception as e:
        logging.error(f"Error in export command: {str(e)}")
        await update.message.reply_text(
            " Sorry, an error occurred while exporting your chat history."
        )

async def text_to_speech_chunk(text: str, output_path: str) -> bool:
    """Convert text to speech using gTTS and save to file."""
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)
        # Save to file
        tts.save(output_path)
        return True
    except Exception as e:
        logging.error(f"Error in text to speech conversion: {str(e)}")
        return False

async def resize_image(image_path, max_size=(800, 800)):
    """Resize image to reduce file size while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
    except Exception as e:
        logging.error(f"Error resizing image: {str(e)}")
        return None

def initialize_genai():
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env file")
    genai.configure(api_key=api_key)

def get_video_insights(video_path):
    """Get insights from a video using Gemini Vision."""
    try:
        logging.info(f"🎥 Processing video: {video_path}")
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Read video file
        with open(video_path, 'rb') as f:
            video_data = f.read()
            
        # Create video part for Gemini
        video_part = {
            'mime_type': 'video/mp4',
            'data': video_data
        }
        
        # Generate prompt for video analysis
        prompt = """
        Analyze this video and provide insights on:
        1. What's happening in the video
        2. Key events or actions
        3. Notable objects or people
        4. Overall context and setting
        
        Please be detailed but concise in your analysis.
        """
        
        # Generate response
        response = model.generate_content([prompt, video_part])
        
        return response.text
        
    except Exception as e:
        logging.error(f"Error in video analysis: {str(e)}")
        raise

MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB

async def analyze_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /analyze_video command and direct video messages."""
    try:
        if not update.message:
            return
            
        # Get video file from either command or direct message
        video = update.message.video
        document = update.message.document

        # If neither video nor document is present, send instructions
        if not video and not document:
            await update.message.reply_text(
                "Please send me a video to analyze! You can either:\n"
                "1. Send the video directly\n"
                "2. Use /analyze_video and attach a video\n\n"
                "📝 Requirements:\n"
                "• Maximum file size: 50MB\n"
                "• Supported formats: MP4, MOV, AVI\n"
                "• Recommended length: 1-3 minutes"
            )
            return

        # Get file ID
        file_id = video.file_id if video else document.file_id if document else None
        if not file_id:
            await update.message.reply_text("Please send a valid video file.")
            return

        # Send initial status
        await update.message.reply_text("Starting video analysis...")

        # Download video
        file = await context.bot.get_file(file_id)
        file_path = os.path.join(MEDIA_FOLDER, f"video_{update.message.from_user.id}_{int(time.time())}.mp4")
        await file.download_to_drive(file_path)

        # Analyze video
        insights = get_insights(file_path)

        # Send results
        await update.message.reply_text(f"Analysis Results:\n\n{insights}")

    except Exception as e:
        await update.message.reply_text(f"Error processing video: {str(e)}")
        
    finally:
        # Cleanup
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

async def setup_commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to set up the bot commands menu."""
    try:
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help message"),
            BotCommand("chat", "Start a chat conversation"),
            BotCommand("settings", "Configure bot settings"),
            BotCommand("togglevoice", "Toggle voice responses"),
            BotCommand("imagine", "Generate an image from text using Replicate"),
            BotCommand("caption", "Generate a detailed caption for an image"),
            BotCommand("enhance", "Enhance your text"),
            BotCommand("describe", "Analyze an image"),
            BotCommand("clear_chat", "Clear chat history"),
            BotCommand("export", "Export chat history"),
            BotCommand("analyze_video", "Analyze a video file"),
            BotCommand("status", "Check bot status"),
            BotCommand("subscribe", "Subscribe to bot updates"),
            BotCommand("unsubscribe", "Unsubscribe from updates"),
            BotCommand("maintenance", "Set bot maintenance mode (Admin only)")
        ]
        await context.bot.set_my_commands(commands)
        await update.message.reply_text("✅ Bot commands have been successfully updated!")
        logging.info("✅ Bot commands registered successfully")
    except Exception as e:
        error_message = f"❌ Failed to register bot commands: {str(e)}"
        await update.message.reply_text(error_message)
        logging.error(error_message)

async def post_init(application: Application) -> None:
    """Post-initialization hook for the bot."""
    try:
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help message"),
            BotCommand("chat", "Start a chat conversation"),
            BotCommand("settings", "Configure bot settings"),
            BotCommand("togglevoice", "Toggle voice responses"),
            BotCommand("imagine", "Generate an image from text using Replicate"),
            BotCommand("caption", "Generate a detailed caption for an image"),
            BotCommand("enhance", "Enhance your text"),
            BotCommand("describe", "Analyze an image"),
            BotCommand("clear_chat", "Clear chat history"),
            BotCommand("export", "Export chat history"),
            BotCommand("analyze_video", "Analyze a video file"),
            BotCommand("status", "Check bot status"),
            BotCommand("subscribe", "Subscribe to bot updates"),
            BotCommand("unsubscribe", "Unsubscribe from updates"),
            BotCommand("maintenance", "Set bot maintenance mode (Admin only)")
        ]
        await application.bot.set_my_commands(commands)
        logging.info("✅ Bot commands registered successfully during initialization")
    except Exception as e:
        logging.error(f"❌ Failed to register bot commands during initialization: {str(e)}")
    
    await notify_subscribers(application, "🟢 Bot is now online and ready!")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle videos sent directly to the bot."""
    await analyze_video_command(update, context)

async def caption_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /caption command for generating image captions."""
    if not update.message:
        return

    # Check if an image was provided
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "Please use this command as a reply to an image with an optional custom prompt.\n"
            "Example:\n"
            "1. Send an image\n"
            "2. Reply to it with `/caption` or `/caption your custom prompt`",
            parse_mode='Markdown'
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()

    session = user_sessions[user_id]
    if not session.replicate_api_key:
        await update.message.reply_text(
            "Please set your Replicate API key in the .env file first.",
            parse_mode='Markdown'
        )
        return

    # Get the custom prompt if provided
    custom_prompt = ' '.join(context.args) if context.args else None

    # Get the largest photo (best quality)
    photo = update.message.reply_to_message.photo[-1]
    
    # Get photo file and generate caption
    try:
        photo_file = await context.bot.get_file(photo.file_id)
        photo_url = photo_file.file_path

        # Send a processing message
        processing_message = await update.message.reply_text("🤔 Analyzing the image...")

        # Generate caption
        success, caption = await image_captioner.generate_caption(photo_url, custom_prompt)
        
        if success:
            await processing_message.edit_text(f"🖼️ Image Analysis:\n\n{caption}")
        else:
            await processing_message.edit_text(f"❌ {caption}")  # caption contains error message
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing image: {str(e)}")

def setup_bot():
    """Set up and configure the bot with all handlers."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("imagine", imagine_command))
    application.add_handler(CommandHandler("caption", caption_command))
    application.add_handler(CommandHandler("enhance", enhance_command))
    application.add_handler(CommandHandler("describe", describe_image))
    application.add_handler(CommandHandler("clear_chat", clear_chat))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("analyze_video", analyze_video_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("maintenance", maintenance_command))
    application.add_handler(CommandHandler("setup_commands", setup_commands_command))

    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    # Add callback query handler for inline keyboard buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add error handler
    application.add_error_handler(error_handler)

    return application

async def run_bot():
    """Run the bot."""
    try:
        # Initialize Gemini AI
        initialize_genai()
        
        # Set up the bot
        application = setup_bot()
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Error in run_bot: {str(e)}")
        raise
    finally:
        # Properly shut down the bot
        await application.stop()

if __name__ == "__main__":
    # Initialize Gemini AI
    initialize_genai()
    # Run the bot using the app.py implementation
    from app import main
    main()