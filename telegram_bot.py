from telegram import Update, Bot, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
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
from database_helper import DatabaseHelper

# Initialize image generator and captioner
image_generator = AIImageGenerator()
image_captioner = ImageCaptioner()

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ROOT_PASSWORD = os.getenv('ROOT_PASSWORD')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))  # Default to 0 if not set

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
if not ROOT_PASSWORD:
    raise ValueError("ROOT_PASSWORD not found in environment variables")
if not ADMIN_USER_ID:
    raise ValueError("ADMIN_USER_ID not found in environment variables")

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

# Initialize database
db = DatabaseHelper()

# Dictionary of available commands and their descriptions
COMMANDS = {
    "/start": "Start the bot",
    "/help": "Show help message",
    "/chat": "Start a chat conversation",
    "/settings": "Configure bot settings",
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
    "/setgroqapi": "Set your Groq API key"
}

# Group commands by category for help menu
COMMAND_CATEGORIES = {
    "🤖 Chat": ['chat', 'clear_chat', 'export'],
    "🎨 Media": ['imagine', 'caption', 'enhance', 'describe', 'analyze_video'],
    "🔊 Settings": ['settings', 'setgroqapi'],
    "📊 Status": ['status', 'subscribe', 'unsubscribe'],
    "ℹ️ General": ['start', 'help'],
    "🔐 Admin": ['maintenance']
}

class UserSession:
    def __init__(self):
        self.conversation_history = []
        self.last_response = None
        self.last_image_prompt = None
        self.last_image_url = None
        self.last_photo = None  # Store last photo for inline keyboard actions
        self.selected_model = "llama3-70b-8192"  # Default Groq model
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.together_api_key = os.getenv('TOGETHER_API_KEY')
        self.last_enhanced_prompt = None
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

# Dictionary to store subscribed users
subscribed_users = set()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if not update.message:
        return

    welcome_message = (
        "🤖 Welcome to OmenFusionAi_Bot!\n\n"
        "🤖 Cereate by Amul Thantharate\n\n"
        "I'm your AI assistant that can help you with various tasks:\n\n"
        "🗣️ Chat - Have natural conversations with AI\n"
        "🎨 Images - Generate and analyze images\n"
        "🎥 Video - Analyze video content\n"
        "📝 Text - Enhance and improve your text\n"
        "📊 Status - Get bot updates and notifications\n\n"
        "Type /help to see all available commands!"
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    if not update.message:
        return
        
    help_text = "🤖 *OmenFusionAi_Bot Commands*\n\n"
    
    # Add regular categories first
    for category, commands in COMMAND_CATEGORIES.items():
        if category != "🔐 Admin":  # Skip admin commands for now
            help_text += f"\n{category}\n"
            for cmd in commands:
                cmd_with_slash = f"/{cmd}"
                if cmd_with_slash in COMMANDS:
                    # Escape special characters
                    description = COMMANDS[cmd_with_slash].replace("(", "\\(").replace(")", "\\)").replace("_", "\\_").replace("-", "\\-").replace(".", "\\.")
                    help_text += f"• `{cmd_with_slash}` \\- {description}\n"
    
    # Add admin commands separately
    if "🔐 Admin" in COMMAND_CATEGORIES:
        help_text += "\n🔐 *Admin Commands*\n"
        for cmd in COMMAND_CATEGORIES["🔐 Admin"]:
            cmd_with_slash = f"/{cmd}"
            if cmd_with_slash in COMMANDS:
                # Escape special characters
                description = COMMANDS[cmd_with_slash].replace("(", "\\(").replace(")", "\\)").replace("_", "\\_").replace("-", "\\-").replace(".", "\\.")
                help_text += f"• `{cmd_with_slash}` \\- {description}\n"
    
    help_text += "\n_For more information about what I can do, type_ `/start`"
    
    try:
        await update.message.reply_text(
            help_text,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        # Fallback to plain text if Markdown fails
        plain_text = help_text.replace('*', '').replace('_', '').replace('`', '').replace('\\', '')
        await update.message.reply_text(plain_text)
        logging.error(f"Error sending help message with Markdown: {str(e)}")

async def setgroqapi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set Groq API key for the user."""
    if not update.message or not context.args:
        await update.message.reply_text(
            "Please provide your Groq API key.\n"
            "Usage: /setgroqapi <your_api_key>\n"
            "Example: /setgroqapi gsk_abcd1234..."
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    
    api_key = context.args[0]
    user_sessions[user_id].groq_api_key = api_key
    
    # Delete the message containing the API key for security
    await update.message.delete()
    
    # Send confirmation
    await update.message.reply_text(
        "✅ Your Groq API key has been set successfully!\n"
        "You can now use the chat features."
    )

async def setreplicateapi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This command is deprecated."""
    await update.message.reply_text(
        "⚠️ This command is deprecated. The bot now uses Together AI for image generation.\n"
        "Please set your Together API key in the .env file."
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
        
        # Store in database
        db.add_or_update_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name
        )
        db.store_chat(user_id, message, response, "llama3-70b-8192")
        
        # Send text response
        await update.message.reply_text(response)
        
        # Add AI response to conversation history
        session.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Store the last response
        session.last_response = response

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
    user_id = update.effective_user.id

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

            # Store in database
            db.add_or_update_user(
                user_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )
            db.store_image_generation(user_id, prompt, enhanced_prompt, "generated_image.png")

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
    if not session.together_api_key:
        await update.message.reply_text(
            " Please set your Together API key first using:\n"
            "`/settogetherkey your_api_key`",
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
        enhancer.together_api_key = session.together_api_key
        
        start_time = time.time()
        success, enhanced_text, error = await enhancer.enhance_text(text)
        total_time = time.time() - start_time
        
        if success and enhanced_text:
            # Store in database
            db.add_or_update_user(
                user_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )
            db.store_text_enhancement(user_id, text, enhanced_text)
            
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
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    
    session = user_sessions[user_id]
    
    await update.message.reply_text(
        " Current Settings:\n\n"
        f"Groq API Key: {' Set' if session.groq_api_key else ' Not Set'}\n"
        f"Together API Key: {' Set' if session.together_api_key else ' Not Set'}\n"
        f"Selected Model: {session.selected_model}"
    )

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

        # Store in database
        db.add_or_update_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name
        )
        db.store_image_description(user_id, file_url, description)

        # Send the text description
        await update.message.reply_text(description)
        logging.info("Text description sent to user")

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
                # Store in database
                db.add_or_update_user(
                    user_id=user_id,
                    username=query.from_user.username,
                    first_name=query.from_user.first_name,
                    last_name=query.from_user.last_name
                )
                db.store_image_caption(user_id, photo_url, caption)
                
                await query.edit_message_text(f"🎨 Creative Caption:\n\n{caption}")
            else:
                await query.edit_message_text(f"❌ Error: {caption}")

    except Exception as e:
        logger.error(f"Error in button callback: {str(e)}")
        await query.edit_message_text("❌ Sorry, something went wrong. Please try again later.")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages and respond with text."""
    if not update.message:
        return

    # Get or create user session
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    
    session = user_sessions[user_id]
    
    # Get the message text
    message_text = update.message.text
    
    try:
        # Generate response using chat function
        response = await interactive_chat(message_text, session.selected_model, session.groq_api_key)
        
        # Send the text response
        await update.message.reply_text(response)
        
    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        logging.error(error_message)
        await update.message.reply_text(error_message)

def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    return user_id == ADMIN_USER_ID

async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle maintenance mode. Only available to admin users."""
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id
    
    # Strict admin check
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text(
            "🚫 Access Denied: This command is restricted to admin use only.",
            parse_mode='Markdown'
        )
        logger.warning(f"Unauthorized maintenance command attempt by user {user_id}")
        return

    try:
        BOT_STATUS["is_maintenance"] = not BOT_STATUS["is_maintenance"]
        status = "enabled" if BOT_STATUS["is_maintenance"] else "disabled"
        
        if BOT_STATUS["is_maintenance"]:
            BOT_STATUS["maintenance_start"] = datetime.now()
            BOT_STATUS["maintenance_end"] = None
            BOT_STATUS["maintenance_message"] = (
                "🛠️ Bot is currently under maintenance.\n"
                "We apologize for the inconvenience.\n"
                "Please try again later."
            )
            
            maintenance_notification = (
                "🔧 *Maintenance Mode Activated*\n\n"
                "The bot is entering maintenance mode.\n"
                "Some features may be temporarily unavailable.\n"
                "We'll notify you once maintenance is complete."
            )
            await notify_subscribers(context.bot, maintenance_notification)
        else:
            BOT_STATUS["maintenance_end"] = datetime.now()
            BOT_STATUS["maintenance_message"] = ""
            
            end_maintenance_notification = (
                "✅ *Maintenance Complete*\n\n"
                "All bot features are now available.\n"
                "Thank you for your patience!"
            )
            await notify_subscribers(context.bot, end_maintenance_notification)
        
        await update.message.reply_text(
            f"✅ Maintenance mode {status}\n"
            f"Status updated by admin {user_id}"
        )
        logger.info(f"Maintenance mode {status} by admin {user_id}")
        
    except Exception as e:
        error_msg = f"Error toggling maintenance mode: {str(e)}"
        logger.error(error_msg)
        await update.message.reply_text(
            f"❌ Error: {error_msg}\n"
            "Please try again or check the logs."
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
    for chat_id in subscribed_users:
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

        # Store in database
        user_id = update.effective_user.id
        db.add_or_update_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name
        )
        db.store_video_analysis(user_id, file_path, insights)

        # Send results
        await update.message.reply_text(f"Analysis Results:\n\n{insights}")

    except Exception as e:
        await update.message.reply_text(f"Error processing video: {str(e)}")
        
    finally:
        # Cleanup
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

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
    if not session.together_api_key:
        await update.message.reply_text(
            "Please set your Together API key in the .env file first.",
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
            # Store in database
            db.add_or_update_user(
                user_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )
            db.store_image_caption(user_id, photo_url, caption)
            
            await processing_message.edit_text(f"🖼️ Image Analysis:\n\n{caption}")
        else:
            await processing_message.edit_text(f"❌ {caption}")  # caption contains error message
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing image: {str(e)}")

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe to bot updates and notifications."""
    if not update.effective_user:
        return
        
    user_id = update.effective_user.id
    if user_id in subscribed_users:
        await update.message.reply_text("You are already subscribed to bot updates! 📬")
        return
        
    subscribed_users.add(user_id)
    
    # Store in database
    db.add_or_update_user(
        user_id=user_id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )
    db.update_subscription(user_id, True)
    
    await update.message.reply_text(
        "✅ You have successfully subscribed to bot updates!\n"
        "You will now receive notifications about:\n"
        "• Bot maintenance and downtime\n"
        "• New features and improvements\n"
        "• Important announcements\n\n"
        "To unsubscribe, use /unsubscribe"
    )

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe from bot updates and notifications."""
    if not update.effective_user:
        return
        
    user_id = update.effective_user.id
    if user_id not in subscribed_users:
        await update.message.reply_text("You are not currently subscribed to bot updates.")
        return
        
    subscribed_users.remove(user_id)
    
    # Update database
    db.update_subscription(user_id, False)
    
    await update.message.reply_text(
        "✅ You have been unsubscribed from bot updates.\n"
        "You will no longer receive notifications.\n\n"
        "To subscribe again, use /subscribe"
    )

async def notify_subscribers(bot: Bot, message: str):
    """Send a notification to all subscribed users."""
    for user_id in subscribed_users:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logging.error(f"Failed to notify user {user_id}: {str(e)}")

async def print_bot_info(bot):
    """Print basic information about the bot"""
    logger.info(f"Bot Username: {bot.username}")
    logger.info(f"Bot ID: {bot.id}")
    logger.info("Bot started successfully!")

def setup_bot():
    """Set up and configure the bot with all handlers."""
    # Configure the application with custom settings
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .connection_pool_size(8)
        .pool_timeout(30.0)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .get_updates_connection_pool_size(8)
        .concurrent_updates(True)
        .build()
    )

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
    application.add_handler(CommandHandler("setgroqapi", setgroqapi_command))

    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))

    return application

def main():
    """Main function to run the bot."""
    try:
        # Initialize Gemini AI
        initialize_genai()
        
        # Set up and run the bot
        application = setup_bot()
        
        # Run the bot
        print("Starting bot...")
        application.run_polling(drop_pending_updates=True)
        
    except KeyboardInterrupt:
        print("Bot stopped by user request")
    except Exception as e:
        print(f"Error running bot: {str(e)}")

if __name__ == "__main__":
    main()