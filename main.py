import asyncio
import os
from dotenv import load_dotenv 
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from loguru import logger
from db import DataBase

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
db = DataBase()

# Mock functions for commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id  # Get the user ID
    logger.debug(f"User ID: {user_id}")  

    help_text = """
    Good day, boss
Here is the list of all available commands:\n
/start or /help - show this help message
/add <token contract> - add token to track
/remove <token contract> - remove token from tracking
/list - list all current tracked tokens
    """
    await update.message.reply_text(help_text)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:  # Check if there are any arguments
        token_contract = ' '.join(context.args)
        logger.debug(f"Token contract added: {token_contract}")
        db.insert_value(update.message.from_user.id, token_contract)

        await update.message.reply_text(f"Token contract added: {token_contract}")
    else:
        await update.message.reply_text("Please provide a token contract address")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:  # Check if there are any arguments
        token_contract = ' '.join(context.args)
        logger.debug(f"Token contract removed: {token_contract}")

        db.remove_value(update.message.from_user.id, token_contract)
        await update.message.reply_text(f"Token contract removed: {token_contract}")
    else:
        await update.message.reply_text("Please provide a token contract address")

async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tokens = db.get_user_tokens(update.message.from_user.id)
    if user_tokens:
        await update.message.reply_text(f"Current tracked tokens:\n{'\n'.join(user_tokens)}")
    else:
        await update.message.reply_text("No tokens are currently being tracked.")

def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("help", start))

    logger.info("Bot is running")
    app.run_polling()

if __name__ == '__main__':
    main()