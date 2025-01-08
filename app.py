import os
import logging
from flask import Flask
import asyncio
from telegram.ext import Application
from dotenv import load_dotenv
from telegram_bot import setup_bot
from threading import Event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variables
application = None
stop_event = Event()

@app.route('/')
def home():
    return 'Bot is running!'

async def run_bot():
    """Run the Telegram bot."""
    global application
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Get bot token and verify
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
            
        logger.info(f"Token length: {len(token)}")
        logger.info(f"Token prefix: {token.split(':')[0]}")
        logger.info(f"Setting up bot with token: {token.split(':')[0]}...")
        
        # Setup bot
        application = await setup_bot()
        
        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Keep running until stop_event is set
        while not stop_event.is_set():
            await asyncio.sleep(1)
            
        # Cleanup
        await application.stop()
        
    except Exception as e:
        logger.error(f"Error in run_bot: {str(e)}")
        raise

def run_flask():
    """Run the Flask app."""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def main():
    """Main function to run both Flask and the bot."""
    import threading
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run bot in the main thread
    asyncio.run(run_bot())

if __name__ == '__main__':
    main()
