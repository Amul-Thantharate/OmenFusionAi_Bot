import os
import logging
import asyncio
from threading import Thread, Event
from flask import Flask
from telegram.ext import Application
from dotenv import load_dotenv
from telegram_bot import setup_bot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global stop event
stop_event = Event()

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    """Run the Flask app."""
    app.run(host='0.0.0.0', port=5000)

async def run_bot():
    """Run the Telegram bot."""
    application = None
    update_offset = None  # Track the last update ID
    try:
        # Set up the bot
        application = setup_bot()
        
        # Start the bot
        await application.initialize()
        await application.start()
        
        # Define allowed update types
        allowed_updates = [
            "message",
            "edited_message",
            "channel_post",
            "edited_channel_post",
            "inline_query",
            "chosen_inline_result",
            "callback_query",
            "shipping_query",
            "pre_checkout_query",
            "poll",
            "poll_answer",
            "my_chat_member",
            "chat_member",
            "chat_join_request"
        ]
        
        # Run polling until stop event is set
        while not stop_event.is_set():
            try:
                updates = await application.bot.get_updates(
                    offset=update_offset,
                    timeout=1,
                    allowed_updates=allowed_updates
                )
                
                for update in updates:
                    await application.process_update(update)
                    # Update the offset to the latest update_id + 1
                    update_offset = update.update_id + 1
                    
            except Exception as e:
                if not stop_event.is_set():  # Only log if not stopping intentionally
                    logger.error(f"Error processing updates: {str(e)}")
                await asyncio.sleep(1)
                
    except Exception as e:
        logger.error(f"Error in run_bot: {str(e)}")
    finally:
        if application:
            try:
                await application.stop()
                logger.info("Bot stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping bot: {str(e)}")

def run_bot_thread():
    """Run the bot in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot())
    except Exception as e:
        logger.error(f"Error in bot thread: {str(e)}")
    finally:
        loop.close()

def main():
    """Main function to run both Flask and the bot."""
    try:
        # Start Flask in a separate thread
        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        # Start bot in a separate thread
        bot_thread = Thread(target=run_bot_thread)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Keep the main thread running
        try:
            while True:
                if not flask_thread.is_alive() or not bot_thread.is_alive():
                    logger.error("One of the threads died. Shutting down...")
                    break
                asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))
        except KeyboardInterrupt:
            logger.info("Shutting down by user request...")
        finally:
            stop_event.set()  # Signal the bot to stop
            flask_thread.join(timeout=5)
            bot_thread.join(timeout=5)
            logger.info("All threads terminated")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == '__main__':
    main()
