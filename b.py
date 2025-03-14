import requests
import time
import schedule
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Function to create an invite link
def create_invite_link(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/exportChatInviteLink"
    response = requests.post(url, data={'chat_id': chat_id})
    return response.json().get('result')

# Function to update the invite link in the channel
def update_invite_link(bot_token, chat_id):
    invite_link = create_invite_link(bot_token, chat_id)
    message = f"New Invite Link: {invite_link}"
    
    # Send the message to the channel
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': message})

# Command to set the chat ID
def set_chat_id(update: Update, context: CallbackContext):
    if context.args:
        chat_id = context.args[0]
        context.user_data['chat_id'] = chat_id
        update.message.reply_text(f"Chat ID set to: {chat_id}")
    else:
        update.message.reply_text("Please provide a chat ID.")

# Command to show help menu
def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Welcome to the Invite Link Bot!\n"
        "Here are the commands you can use:\n"
        "/set_chat_id <chat_id> - Set the chat ID for the channel.\n"
        "/help - Show this help menu.\n"
        "The bot will automatically generate and update the invite link at the specified interval."
    )
    update.message.reply_text(help_text)

# Function to schedule the invite link updates
def schedule_updates(bot_token, chat_id, interval):
    schedule.every(interval).minutes.do(update_invite_link, bot_token=bot_token, chat_id=chat_id)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Replace with your bot token
    BOT_TOKEN = '7549968540:AAFqi_7DyheAzsM49_jSxQHMYvz0ynjjn7E'
    
    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("set_chat_id", set_chat_id))
    dp.add_handler(CommandHandler("help", help_command))

    # Start the bot
    updater.start_polling()

    # Set the interval for updates (in minutes)
    INTERVAL = 60  # Update every hour

    # Start scheduling updates with a default chat ID
    chat_id = None
    while True:
        if 'chat_id' in updater.dispatcher.user_data:
            chat_id = updater.dispatcher.user_data['chat_id']
            schedule_updates(BOT_TOKEN, chat_id, INTERVAL)
        time.sleep(1)
