import logging
import threading
import time
import os
import sys
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configuration Section
TELEGRAM_BOT_TOKEN = "7549968540:AAFqi_7DyheAzsM49_jSxQHMYvz0ynjjn7E"  # Replace with your Telegram bot token
MONGODB_URI = "mongodb+srv://akashrabha2005:781120@cluster0.pv6yd2f.mongodb.net/"  # MongoDB connection string
DATABASE_NAME = "link_timer_db"  # Name of the database
COLLECTION_NAME = "user_links"  # Name of the collection
OWNER_ID = 7210185648  # Replace with your Telegram user ID

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Welcome! Use /updatelink <new_link> to set a link and /starttimer <seconds> <link> to set a timer.')

async def update_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Update the link for the user."""
    if len(context.args) != 1:
        await update.message.reply_text('Usage: /updatelink <new_link>')
        return

    new_link = context.args[0]
    
    # Validate the link
    if not new_link.startswith("http://") and not new_link.startswith("https://"):
        await update.message.reply_text('Please provide a valid URL starting with http:// or https://')
        return

    # Save the new link to the database
    user_id = update.message.from_user.id
    collection.update_one({'user_id': user_id}, {'$set': {'link': new_link}}, upsert=True)
    await update.message.reply_text(f'Link updated successfully to: {new_link}')

async def start_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a timer that updates the link at regular intervals."""
    if len(context.args) != 2:
        await update.message.reply_text('Usage: /starttimer <seconds> <link>')
        return

    try:
        interval = int(context.args[0])
        link = context.args[1]
    except ValueError:
        await update.message.reply_text('Please provide a valid number for seconds.')
        return

    if interval <= 0:
        await update.message.reply_text('Please provide a positive number for seconds.')
        return

    # Start a new thread for the timer
    threading.Thread(target=timer_thread, args=(update.message.from_user.id, interval, link)).start()
    await update.message.reply_text(f'Timer started! The link will be updated every {interval} seconds.')

def timer_thread(user_id, interval, link):
    """Thread function to update the link at regular intervals."""
    while True:
        time.sleep(interval)
        # Here you would implement the logic to update the link
        print(f'Link updated for user {user_id}: {link}')  # Replace with actual update logic

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Restart the bot if the user is the owner."""
    if update.message.from_user.id == OWNER_ID:
        await update.message.reply_text('Restarting the bot...')
        os.execv(sys.executable, ['python'] + sys.argv)  # Restart the bot
    else:
        await update.message.reply_text('You do not have permission to restart the bot.')

def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("updatelink", update_link))
    application.add_handler(CommandHandler("starttimer", start_timer))
    application.add_handler(CommandHandler("restart", restart))  # Add the restart command

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
