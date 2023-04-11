import os

from dotenv import load_dotenv
from telegram import Update, InlineQueryResultCachedSticker
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext, InlineQueryHandler

import stickergen

# Load the environment variables

load_dotenv()

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv('PORT', 5000))
HEROKU_PATH = os.getenv('HEROKU_PATH')
LOG_GROUP_ID = int(os.getenv('LOG_GROUP_ID'))


async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Yo la zone")
    return


async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Contactez @eliorpap pour plus d\'infos !')
    return


async def agep(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    # Get the text from the message and generate the sticker from it (or use a default text)
    text_parts = update.message.text.split(' ', 1)
    if len(text_parts) > 1:
        _, text = text_parts
    else:
        text = 'Yo wtf - GIBE TEXT !'
    sticker = stickergen.gen_sticker_agep(text)
    await update.message.reply_sticker(sticker)
    return


async def inline(update: Update, context: CallbackContext) -> None:
    """Generate a sticker based on the inline query."""
    # Get the text from the inline query and generate the sticker from it (or use a default text)
    query = update.inline_query.query
    if not query:
        return
    sticker = stickergen.gen_sticker_agep(query)
    sticker_message = await context.bot.send_sticker(chat_id=LOG_GROUP_ID, sticker=sticker)
    result = InlineQueryResultCachedSticker(
        id=query,
        sticker_file_id=sticker_message.sticker.file_id,
    )
    await update.inline_query.answer([result])
    return


async def dump(update: Update, context: CallbackContext) -> None:
    """Dump the update object."""
    await update.message.reply_text(f"```{update}```", parse_mode=ParseMode.MARKDOWN_V2)
    return


def main() -> None:
    """Start the bot."""
    print("Going live!")

    # Create application
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("agep", agep))
    application.add_handler(CommandHandler("dump", dump))

    # Set up the InlineQueryHandler for the agep function
    application.add_handler(InlineQueryHandler(inline))

    # Start the Bot
    print("Bot starting...")
    if os.environ.get('ENV') == 'DEV':
        application.run_polling()
    elif os.environ.get('ENV') == 'PROD':
        application.run_webhook(listen="0.0.0.0",
                                port=int(PORT),
                                webhook_url=HEROKU_PATH)
    return


if __name__ == '__main__':
    main()
