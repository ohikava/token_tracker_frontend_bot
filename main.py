import asyncio
from http import HTTPStatus
import os
from dotenv import load_dotenv 
from telegram import Update
from telegram.ext import ApplicationBuilder,ExtBot,TypeHandler, CallbackContext, CommandHandler, ContextTypes
from loguru import logger
from fastapi import FastAPI, Response, Request
from db import DataBase
from contextlib import asynccontextmanager
from dataclasses import dataclass

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_URL = os.getenv("SERVER_URL")
db = DataBase()

@dataclass
class Notify:
    users: list[str]
    message: str

class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """
    @classmethod
    def from_update(cls, update: object, application: "Application") -> "CustomContext":
        if isinstance(update, Notify):
            return cls(application=application)
        return super().from_update(update, application)

async def notify_users(update: Notify, context: CustomContext) -> None:
    for user_id in update.users:
        await context.bot.send_message(chat_id=user_id, text=update.message)

context_types = ContextTypes(context=CustomContext)

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
print(f"{SERVER_URL}/telegram")
def main() -> None:
    ptb = ApplicationBuilder().token(BOT_TOKEN).updater(None).context_types(context_types).build()

    # Register command handlers
    ptb.add_handler(CommandHandler("start", start))
    ptb.add_handler(CommandHandler("add", add))
    ptb.add_handler(CommandHandler("remove", remove))
    ptb.add_handler(CommandHandler("list", list_items))
    ptb.add_handler(CommandHandler("help", start))
    ptb.add_handler(TypeHandler(type=Notify, callback=notify_users))

    @asynccontextmanager
    async def app_lifespan(app: FastAPI):
        print('Init lifespan')
        await ptb.bot.set_webhook(f"{SERVER_URL}/telegram")
        async with ptb:
            await ptb.start()
            yield
            print('close lifespan')
            await ptb.stop()

    logger.info("Bot is running")
    app = FastAPI(lifespan=app_lifespan)
    @app.post("/telegram")
    async def telegram(request: Request) -> Response:
        body = await request.json()
        await ptb.update_queue.put(Update.de_json(data=body, bot = ptb.bot))
        return Response(status_code=HTTPStatus.OK)
    @app.get("/healthchek")
    async def healthchek(request: Request) -> Response:
        return Response(content='bot is working!', status_code=HTTPStatus.OK)
    
    @app.post("/notify")
    async def notify(request: Request) -> Response:
        body = await request.json()
        users = db.get_users_by_token(body['token'])
        logger.debug(f"Users: {users}")
        await ptb.update_queue.put(Notify(users=users, message=body['message']))
        return Response(status_code=HTTPStatus.OK)
    
    # app.run_polling()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)

if __name__ == '__main__':
    main()