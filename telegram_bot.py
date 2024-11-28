#!/usr/bin/env python3
"""
AIFusionBot - Telegram Bot Implementation
Handles all bot commands and interactions
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from io import BytesIO
import time
from typing import Optional
from dotenv import load_dotenv
from main import interactive_chat, save_chat_history, generate_image, generate_image_together
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variable for user sessions
user_sessions = {}

# Bot command descriptions
COMMANDS = {
    'start': 'Start AIFusionBot',
    'help': 'Show available commands',
    'chat': 'Start AI conversation',
    'image': 'Generate a basic image',
    'imagine': 'Create high-quality image',
    'setgroqkey': 'Set Groq API key',
    'settogetherkey': 'Set Together AI key',
    'settings': 'View current settings',
    'export': 'Export chat history',
    'clear': 'Clear chat history',
    'temperature': 'Adjust response creativity',
    'tokens': 'Set maximum response length'
}

class UserSession:
    def __init__(self):
        self.model_type = "groq"
        self.temperature = 0.5
        self.max_tokens = 1024
        self.chat_history = []
        self.groq_api_key = None
        self.together_api_key = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    logger.info(f"Start command received from user {update.effective_user.id}")
    welcome_message = (
        "👋 Welcome to AIFusionBot!\n\n"
        "I'm your advanced AI assistant powered by Groq and Together AI. "
        "I can help you with:\n\n"
        "🗣️ Natural conversations\n"
        "🎨 Image generation\n"
        "📝 Chat management\n\n"
        "Type /help to see all available commands!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    logger.info(f"Help command received from user {update.effective_user.id}")
    help_text = "🤖 AIFusionBot Commands:\n\n"
    for cmd, desc in COMMANDS.items():
        help_text += f"/{cmd} - {desc}\n"
    await update.message.reply_text(help_text)

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
        "You can now use all bot features.\n"
        "Try `/chat Hello!` or `/image sunset`",
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
    if not context.args:
        await update.message.reply_text("Please provide a message after /chat")
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()

    session = user_sessions[user_id]
    message = ' '.join(context.args)

    try:
        # Send typing action
        await update.message.chat.send_action(action="typing")

        response = interactive_chat(
            text=message,
            temperature=session.temperature,
            max_tokens=session.max_tokens,
            model_type="groq",
            stream=False,
            api_key=session.groq_api_key
        )

        # Store in chat history
        session.chat_history.append({"role": "user", "content": message})
        session.chat_history.append({"role": "assistant", "content": response})

        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in chat_command: {str(e)}")
        await update.message.reply_text(f"Sorry, an error occurred: {str(e)}")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /image command."""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "Please provide a description after /image\n"
            "Example: `/image sunset over mountains`",
            parse_mode='Markdown'
        )
        return

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()

    prompt = ' '.join(context.args)

    # Send a message indicating that image generation has started
    progress_message = await update.message.reply_text("🎨 Generating your image... Please wait.")

    try:
        success, image_bytes, message = generate_image(prompt)

        if success and image_bytes:
            # Send the generated image directly from bytes
            await update.message.reply_photo(
                photo=BytesIO(image_bytes),
                caption=f"🎨 Generated image for: {prompt}\n⏱️ {message}"
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

async def imagine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /imagine command for Together AI image generation."""
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

    if not user_sessions[user_id].together_api_key:
        await update.message.reply_text(
            "⚠️ Please set your Together API key first using:\n"
            "`/settogetherkey your_api_key`",
            parse_mode='Markdown'
        )
        return

    prompt = ' '.join(context.args)

    # Send a message indicating that image generation has started
    progress_message = await update.message.reply_text(
        "🎨 Generating your high-quality image with Together AI... Please wait."
    )

    try:
        success, image_bytes, message = generate_image_together(
            prompt,
            api_key=user_sessions[user_id].together_api_key
        )

        if success and image_bytes:
            # Send the generated image directly from bytes
            await update.message.reply_photo(
                photo=BytesIO(image_bytes),
                caption=f"✨ Generated with Together AI:\n{prompt}\n\n⏱️ {message}"
            )
        else:
            await update.message.reply_text(f"❌ Failed to generate image: {message}")
    except Exception as e:
        logger.error(f"Error in Together image generation: {str(e)}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong while generating the image. Please try again later."
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
    settings_text = (
        f"*Current Settings:*\n"
        f"Model: Groq\n"
        f"Temperature: {session.temperature}\n"
        f"Max Tokens: {session.max_tokens}\n"
        f"Groq API Key: {'✅ Set' if session.groq_api_key else '❌ Not Set'}\n"
        f"Together API Key: {'✅ Set' if session.together_api_key else '❌ Not Set'}\n"
    )
    await update.message.reply_text(settings_text, parse_mode='Markdown')

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /save command."""
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("No chat history to save.")
        return

    session = user_sessions[user_id]
    if not session.chat_history:
        await update.message.reply_text("No chat history to save.")
        return

    try:
        # Save chat history
        filename = save_chat_history(
            messages=session.chat_history,
            model_type="groq",
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
            user_sessions[user_id].chat_history = []
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
    if user_id not in user_sessions or not user_sessions[user_id].chat_history:
        await update.message.reply_text("No chat history to export.")
        return

    # Send "processing" message
    processing_msg = await update.message.reply_text("📤 Processing your export request...")

    try:
        success, message, file_bytes = save_chat_history(
            user_sessions[user_id].chat_history,
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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    if update and isinstance(update, Update) and update.effective_message:
        text = "Sorry, an error occurred while processing your request."
        await update.effective_message.reply_text(text)

def setup_bot(token: str) -> Application:
    """Initialize and configure the AIFusionBot bot"""
    try:
        logger.info("Setting up bot application...")
        # Create application with specific defaults for polling
        app = (
            Application.builder()
            .token(token)
            .concurrent_updates(True)
            .build()
        )

        # Add command handlers
        app.add_handler(CommandHandler('start', start_command))
        app.add_handler(CommandHandler('help', help_command))
        app.add_handler(CommandHandler('setgroqkey', setgroqkey_command))
        app.add_handler(CommandHandler('settogetherkey', settogetherkey_command))
        app.add_handler(CommandHandler('chat', chat_command))
        app.add_handler(CommandHandler('image', image_command))
        app.add_handler(CommandHandler('imagine', imagine_command))
        app.add_handler(CommandHandler('settings', settings_command))
        app.add_handler(CommandHandler('export', export_command))
        app.add_handler(CommandHandler('temperature', temperature_command))
        app.add_handler(CommandHandler('clear', clear_command))

        # Add callback query handler for buttons
        app.add_handler(CallbackQueryHandler(button_callback))

        # Add error handler
        app.add_error_handler(error_handler)

        logger.info("Bot setup completed successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to setup AIFusionBot bot: {str(e)}")
        raise

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Error: Please set TELEGRAM_BOT_TOKEN in your .env file")
        exit(1)
    
    # Create and run the bot in polling mode
    application = setup_bot(TELEGRAM_BOT_TOKEN)
    print("Starting Telegram bot in polling mode...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)