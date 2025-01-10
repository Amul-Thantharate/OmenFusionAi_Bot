from telegram import Update
from telegram.ext import ContextTypes
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Store chat histories
chat_histories = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if not update.message:
        return
        
    welcome_message = (
        "👋 Hello! I'm OmenFusionAi_Bot, your AI-powered assistant. Here's what I can do:\n\n"
        "🤖 Chat - Have natural conversations\n"
        "🎨 Generate Images - Create art from descriptions\n"
        "📝 Caption Images - Describe images in detail\n"
        "🔍 Analyze Videos - Get insights from video content\n"
        "🗣️ Transcribe Audio - Convert speech to text in multiple languages\n\n"
        "Type /help to see all available commands!"
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message."""
    help_text = "*Available Commands*\n\n"
    
    # Add regular categories first
    for category, commands in COMMAND_CATEGORIES.items():
        if category != "🔧 Admin":  # Skip admin commands for now
            help_text += f"\n{category}\n"
            for cmd in commands:
                cmd_with_slash = f"/{cmd}"
                if cmd_with_slash in COMMANDS:
                    description = COMMANDS[cmd_with_slash].replace("_", "\\_")  # Escape underscores
                    help_text += f"• `{cmd_with_slash}` \\- {description}\n"
                    
                    # Add extra help for transcribe command
                    if cmd == "transcribe":
                        help_text += "  _Usage: Reply to an audio with_ `/transcribe [language_code]`\n"
                        help_text += "  _Example:_ `/transcribe es-ES` _for Spanish_\n"
                        help_text += "  _Note: Maximum audio size is 20MB_\n"
    
    try:
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Error sending help message: {str(e)}")
        # Fallback to plain text if markdown fails
        await update.message.reply_text(help_text.replace("*", "").replace("_", "").replace("`", ""))

async def clear_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear chat history for the current user."""
    if not update.message:
        return
        
    user_id = update.message.from_user.id
    if user_id in chat_histories:
        chat_histories[user_id] = []
        await update.message.reply_text("✨ Chat history cleared!")
    else:
        await update.message.reply_text("No chat history to clear.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages sent directly to the bot."""
    await transcribe_command(update, context)

# Export the handlers
__all__ = [
    'start_command',
    'help_command',
    'clear_chat_command',
    'handle_voice',
]
