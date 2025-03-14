import logging
import threading
import time
import os
import sys
from pymongo import MongoClient
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime, timedelta

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

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Welcome! Use /updatelink <new_link> to set a link, /starttimer <seconds> <link> to set a timer, and /addpremium <user_id> <days> <hours> to grant premium access.')

def update_link(update: Update, context: CallbackContext) -> None:
    """Update the link for the user."""
    if len(context.args) != 1:
        update.message.reply_text('Usage: /updatelink <new_link>')
        return

    new_link = context.args[0]
    
    # Validate the link
    if not new_link.startswith("http://") and not new_link.startswith("https://"):
        update.message.reply_text('Please provide a valid URL starting with http:// or https://')
        return

    # Save the new link to the database
    user_id = update.message.from_user.id
    collection.update_one({'user_id': user_id}, {'$set': {'link': new_link}}, upsert=True)
    update.message.reply_text(f'Link updated successfully to: {new_link}')

def start_timer(update: Update, context: CallbackContext) -> None:
    """Start a timer that updates the link at regular intervals."""
    if len(context.args) != 2:
        update.message.reply_text('Usage: /starttimer <seconds> <link>')
        return

    try:
        interval = int(context.args[0])
        link = context.args[1]
    except ValueError:
        update.message.reply_text('Please provide a valid number for seconds.')
        return

    if interval <= 0:
        update.message.reply_text('Please provide a positive number for seconds.')
        return

    # Start a new thread for the timer
    threading.Thread(target=timer_thread, args=(update.message.from_user.id, interval, link)).start()
    update.message.reply_text(f'Timer started! The link will be updated every {interval} seconds.')

def timer_thread(user_id, interval, link):
    """Thread function to update the link at regular intervals."""
    while True:
        time.sleep(interval)
        # Here you would implement the logic to update the link
        # For demonstration, we just print the link
        print(f'Link updated for user {user_id}: {link}')  # Replace with actual update logic

def add_premium(update: Update, context: CallbackContext) -> None:
    """Add premium access to a user for a specified duration."""
    if update.message.from_user.id != OWNER_ID:
        update.message.reply_text('You do not have permission to use this command.')
        return

    if len(context.args) != 3:
        update.message.reply_text('Usage: /addpremium <user_id> <days> <hours>')
        return

    try:
        user_id = int(context.args[0])
        days = int(context.args[1])
        hours = int(context.args[2])
    except ValueError:
        update.message.reply_text('Please provide valid numbers for user_id, days, and hours.')
        return

    # Calculate the expiration date
    expiration_date = datetime.now() + timedelta(days=days, hours=hours)

    # Update the user's premium status in the database
    collection.update_one({'user_id': user_id}, {'$set': {'premium_until': expiration_date}}, upsert=True)
    update.message.reply_text(f'Premium access granted to user {user_id} until {expiration_date}.')

def restart(update: Update, context: CallbackContext) -> None:
    """Restart the bot if the user is the owner."""
    if update.message.from_user.id == OWNER_ID:
        update.message.reply_text('Restarting the bot...')
        os.execv(sys.executable, ['python'] + sys.argv)  # Restart the bot
    else:
        update.message.reply_text('You do not have permission to restart the bot.')

def main() -> None:
    """Start the bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("updatelink", update_link))
    dispatcher.add_handler(CommandHandler("starttimer", start_timer))
    dispatcher.add_handler(CommandHandler("addpremium", add_premium))  # Add the addpremium command
    dispatcher.add_handler(CommandHandler("restart", restart))  # Add the restart command

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
