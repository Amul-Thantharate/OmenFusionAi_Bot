from flask import Flask, request, jsonify
import os
import logging
import threading
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application
from telegram_bot import setup_bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables!")

logger.info("Token details:")
logger.info(f"Token length: {len(TOKEN)}")
logger.info(f"Token prefix: {TOKEN.split(':')[0] if ':' in TOKEN else 'Invalid format'}")

if not TOKEN.count(':') == 1:
    raise ValueError("Invalid token format. Token should contain exactly one ':'")

bot_id, token_suffix = TOKEN.split(':')
if not bot_id.isdigit():
    raise ValueError("Invalid token format. Bot ID part should be numeric")
if len(token_suffix) < 30:  # Typical token suffix is longer than 30 characters
    raise ValueError("Invalid token format. Token suffix seems too short")

logger.info(f"Setting up bot with token: {TOKEN[:10]}...")

app = Flask(__name__)

def run_bot():
    """Run the Telegram bot in the current thread"""
    try:
        # Create and set event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def start_bot():
            try:
                # Initialize bot
                application = await setup_bot(TOKEN)
                
                # Start polling
                await application.initialize()
                await application.start()
                await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
                
                # Keep the application running
                while True:
                    try:
                        await asyncio.sleep(1)
                    except asyncio.CancelledError:
                        break
                
            except Exception as e:
                logger.error(f"Error in start_bot: {str(e)}")
                raise
            finally:
                try:
                    await application.stop()
                except Exception as e:
                    logger.error(f"Error stopping application: {str(e)}")
        
        # Run the bot
        loop.run_until_complete(start_bot())
        
    except Exception as e:
        logger.error(f"Error in run_bot: {str(e)}")
    finally:
        try:
            # Clean up pending tasks
            pending = asyncio.all_tasks(loop)
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception as e:
            logger.error(f"Error cleaning up tasks: {str(e)}")
        finally:
            try:
                loop.close()
            except Exception as e:
                logger.error(f"Error closing loop: {str(e)}")

def run_app():
    """Run the Flask app and Telegram bot"""
    try:
        # Start bot in a separate thread
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Run Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
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
