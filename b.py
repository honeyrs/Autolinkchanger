import requests
import time
import schedule
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Global variable to store the message ID of the last sent invite link
last_message_id = None

# Function to create an invite link
def create_invite_link(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/exportChatInviteLink"
    response = requests.post(url, data={'chat_id': chat_id})
    return response.json().get('result')

# Function to update the invite link in the channel
def update_invite_link(bot_token, chat_id):
    global last_message_id
    invite_link = create_invite_link(bot_token, chat_id)
    message = f"New Invite Link: {invite_link}"
    
    # Send or edit the message in the channel
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage" if last_message_id is None else f"https://api.telegram.org/bot{bot_token}/editMessageText"
    
    if last_message_id is None:
        response = requests.post(url, data={'chat_id': chat_id, 'text': message})
        last_message_id = response.json().get('result', {}).get('message_id')
    else:
        requests.post(url, data={'chat_id': chat_id, 'message_id': last_message_id, 'text': message})

# Command to set the chat ID
async def set_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        chat_id = context.args[0]
        context.user_data['chat_id'] = chat_id
        await update.message.reply_text(f"Chat ID set to: {chat_id}")
    else:
        await update.message.reply_text("Please provide a chat ID.")

# Command to set the update interval
async def set_update_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            interval = int(context.args[0])
            context.user_data['interval'] = interval
            await update.message.reply_text(f"Update interval set to: {interval} minutes.")
        except ValueError:
            await update.message.reply_text("Please provide a valid number for the interval.")
    else:
        await update.message.reply_text("Please provide an interval in minutes.")

# Command to show help menu
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Welcome to the Invite Link Bot!\n"
        "Here are the commands you can use:\n"
        "/set_chat_id <chat_id> - Set the chat ID for the channel.\n"
        "/set_update_interval <minutes> - Set the interval for updating the invite link.\n"
        "/help - Show this help menu.\n"
        "The bot will automatically generate and update the invite link at the specified interval."
    )
    await update.message.reply_text(help_text)

# Function to schedule the invite link updates
def schedule_updates(bot_token, chat_id, interval):
    schedule.every(interval).minutes.do(update_invite_link, bot_token=bot_token, chat_id=chat_id)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Replace with your bot token
    BOT_TOKEN = '7549968540:AAFqi_7DyheAzsM49_jSxQHMYvz0ynjjn7E'
    
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("set_chat_id", set_chat_id))
    application.add_handler(CommandHandler("set_update_interval", set_update_interval))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    application.run_polling()

    # Set the default interval for updates (in minutes)
    INTERVAL = 60  # Default update every hour

    # Start scheduling updates with a default chat ID
    chat_id = None
    while True:
        if 'chat_id' in application.user_data:
            chat_id = application.user_data['chat_id']
            interval = application.user_data.get('interval', INTERVAL)
            schedule_updates(BOT_TOKEN, chat_id, interval)
        time.sleep(1)
