from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application
from telegram_bot import setup_bot
import logging
import asyncio
import threading

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize bot
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables!")

logger.info(f"Setting up bot with token: {TOKEN[:5]}...")
bot_app = setup_bot(TOKEN)

async def run_telegram_bot():
    """Run the Telegram bot"""
    try:
        logger.info("Starting Telegram bot...")
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error running Telegram bot: {str(e)}")
        raise

def run_bot_with_loop():
    """Run the bot with its own event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_telegram_bot())

def run_app():
    """Run the Flask app with the bot"""
    try:
        # Start the Telegram bot in a separate thread
        bot_thread = threading.Thread(target=run_bot_with_loop)
        bot_thread.daemon = True
        bot_thread.start()

        # Run Flask app
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
    except Exception as e:
        logger.error(f"Error running app: {str(e)}")
        raise

@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    if request.method == 'POST':
        try:
            update = Update.de_json(request.get_json(force=True), bot_app.bot)
            bot_app.process_update(update)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405

if __name__ == '__main__':
    run_app()