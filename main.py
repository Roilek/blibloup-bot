import argparse
import asyncio
import datetime
import os
import uuid

import telegram
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultCachedSticker, InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext, InlineQueryHandler

from helpers import qrcodes, database, scrapping, stickergen

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
    text = "Vous pouvez utiliser les commandes suivantes !\n"
    text += "/agep <text> : génère un sticker avec le texte donné\n"
    text += "/cdd : affiche les candidatures en cours\n"
    text += "/reg cdd : recevoir une notification des nouvelles candidatures cdd\n"
    text += "/qr <url> : génère un qr code avec l'url donné (ou n'importe quel texte)\n"
    text += "/decode : décode le QR code donné\n"
    text += "/vcard : créer un qr code de partage d'un contact\n"
    text += "/help : affiche ce message\n"
    await update.message.reply_text(text)
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


async def register(update: Update, context: CallbackContext) -> None:
    """Register a new user."""
    _, text = update.message.text.split(' ', 1)
    database.subscribe_user(update.message.from_user.id, update.effective_user.first_name, text)
    await update.message.reply_text(f"Magnifique ! Tu recevras désormais les notifications qui concernent la fonctionnalité {text}!")
    return


async def stop_function(update: Update, context: CallbackContext) -> None:
    """Unsubscribe people who using a specific function."""
    _, function = update.message.text.split(' ', 1)
    users = database.get_subscribed_users(function)
    for user in users:
        database.unsubscribe_user(user['_id'], function)
        await context.bot.send_message(chat_id=user['_id'], text=f"Un·e admin a désactivé les notifications pour la fonctionnalité {function} ! Tu as été désabonné·e !")
    return


async def candidatures(update: Update, context: CallbackContext) -> None:
    """Send a message with all the candidatures."""
    await update.message.reply_text(scrapping.get_html_candidats(), parse_mode=ParseMode.HTML)
    return


async def qr(update: Update, context: CallbackContext) -> None:
    """Send a qr code with the given data encoded"""
    text_parts = update.message.text.split(' ', 1)
    if len(text_parts) > 1:
        _, text = text_parts
        qr_code = qrcodes.qr_from_text(text)
        await update.message.reply_photo(qr_code)
    else:
        text = "Pour créer qr code, envoyer /qr suivi du text à encoder\n"
        await update.message.reply_text(text)
        return


async def decode(update: Update, context: CallbackContext) -> None:
    """Decode the given qr code"""
    text = "Pas encore implémenté. Vous pouvez envoyer votre QR à @QRcodegen_bot pour le décoder !"
    await update.message.reply_text(text)
    return


async def vcard(update: Update, context: CallbackContext) -> None:
    """Send a vcard qr code with the given data encoded"""
    text_parts = update.message.text.split(' ', 1)
    fields = {
        'Prénom': '',
        'Nom': '',
        'Numéro de téléphone': '',
        'Adresse e-mail': '',
        'Nom de l\'entreprise': '',
        'URL du site web': '',
    }
    if len(text_parts) > 1:
        _, text = text_parts
        text.split('\n')
        for line in text.split('\n')[1:]:
            if line == "Done":
                break
            key, value = line.split(' : ', 1)
            fields[key] = value
        vcard_dict = {
            'fn': fields['Nom'] + ',' + fields['Prénom'],  # Nom complet
            'n': fields['Nom']+';'+fields['Prénom']+';;;',  # Nom
            'tel': fields['Numéro de téléphone'],  # Numéro de téléphone
            'email': fields['Adresse e-mail'],  # Adresse e-mail
            'org': fields['Nom de l\'entreprise'],  # Nom de l'entreprise
            'url': fields['URL du site web']  # URL du site web
        }
        qr_vcard = qrcodes.vcard_from_dict(vcard_dict)
        print("Sending vcard QR")
        await update.message.reply_photo(qr_vcard)
    else:
        text = "Pour créer un contact vcard, vous pouvez copier le message compléter les champs appropriés (renseigner au moins le nom ou le prénom, le reste est optionnel)\n"
        await update.message.reply_text(text)
        text = "/vcard \n"
        for key, value in fields.items():
            text += f"{key} : {value}\n"
        text += "Done"
        await update.message.reply_text(text)
    return


async def inline(update: Update, context: CallbackContext) -> None:
    """Generate a sticker based on the inline query."""
    # Get the text from the inline query and generate the sticker from it (or use a default text)
    query = update.inline_query.query
    if not query:
        return

    result = []

    if query == 'cdd':
        html_text = scrapping.get_html_candidats()
        result.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title='Les candidatures à ce jour !',
            input_message_content=InputTextMessageContent(html_text, parse_mode='HTML')
        ))
    else:
        sticker = stickergen.gen_sticker_agep(query)
        sticker_message = await context.bot.send_sticker(chat_id=LOG_GROUP_ID, sticker=sticker)
        result.append(InlineQueryResultCachedSticker(
            id=str(uuid.uuid4()),
            sticker_file_id=sticker_message.sticker.file_id,
        ))

    await update.inline_query.answer(result, cache_time=0)
    return


async def dump(update: Update, context: CallbackContext) -> None:
    """Dump the update object."""
    await update.message.reply_text(f"```{update}```", parse_mode=ParseMode.MARKDOWN_V2)
    return


async def auto_candidatures() -> None:
    bot = telegram.Bot(token=TOKEN)
    text = scrapping.get_html_candidats()
    if text != database.get_ref_message("cdd"):
        print("New candidature ! Sending to people")
        database.set_ref_message("cdd", text)
        users = database.get_subscribed_users("cdd")
        text = "Timestamp : " + str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")) + "\nNouvelle candidature !\n\n" + text
        for user in users:
            try:
                await bot.send_message(chat_id=user['_id'], text=text, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(e)
        return
    else:
        print("No new candidature !")
        return


def main() -> None:
    """Start the bot."""
    print("Going live!")

    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("function",
                        nargs='?',
                        help="The function to execute",
                        choices=["cdd"])
    args = parser.parse_args()

    # If a function is specified, execute it and exit
    if args.function == "cdd":
        asyncio.run(auto_candidatures())
        return

    # Create application
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("agep", agep))
    application.add_handler(CommandHandler("reg", register))
    application.add_handler(CommandHandler("stop", stop_function))
    application.add_handler(CommandHandler("cdd", candidatures))
    application.add_handler(CommandHandler("qr", qr))
    application.add_handler(CommandHandler("decode", decode))
    application.add_handler(CommandHandler("vcard", vcard))
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
    database.setup()
    main()
