from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
import asyncio
import argparse

import telegram
from telegram import Update, InlineQueryResultCachedSticker
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, CallbackContext
from telegram.constants import ParseMode

from new_helpers import qrcodes, messages, mycalendar, ia, mytelegram, database
from helpers import stickergen
from models.enumerations import Frequency
from models.subscription import Subscription
from new_helpers.mytelegram import SEPARATOR

load_dotenv()

TOKEN = os.getenv('TOKEN')
PORT = int(os.getenv('PORT', 5000))
HEROKU_PATH = os.getenv('HEROKU_PATH')
LOG_GROUP_ID = os.getenv('LOG_GROUP_ID')

# start function
async def start(update: Update, context: CallbackContext) -> None:
    text = 'Hey there! I\'m Blibloup bot and I can do a loooooot of things! \n'
    text += 'Send me /help to see all the things I can do! \n'
    await update.message.reply_text(text)
    return

# help function
async def help_command(update: Update, context: CallbackContext) -> None:
    text = 'Here are the things I can do: \n'
    text += '/start : Start the bot \n'
    text += '/help: Show this message \n'
    text += '/forget : Forget about you (delete you data!)\n'
    text += '/agep : Generate a sticker with AGEPoly font\n'
    text += '/qr : Generate a QRCode for text, url\n'
    text += '/vcard : Generate a QRCode for contact info\n'
    text += '/wifi : Generate a QRCode for wifi connection\n'
    text += '/ics : Generate an ICS file for an event\n'
    text += '/gpt : Generate a text with ChatGPT\n'
    text += '/subhelp : Manage subcriptions to periodic prompting\n'
    text += '\n'
    text += 'You can also use me directly from any chat by typing in @blibloup_bot [text to stickerize]\n'
    await update.message.reply_text(text)
    return

# sub-hekp function
async def sub_help(update: Update, context: CallbackContext) -> None:
    text = 'Here are the things I can do regarding subscriptions: \n'
    text += '/subhelp: Show this message \n'
    text += '/sub : Subscribe to periodic prompting\n'
    text += '/unsub : Unsubscribe from periodic prompting\n'
    text += '/del : Delete a periodic prompting\n'
    text += 'For all commands, please send /help'
    await update.message.reply_text(text)
    return

# forget function
async def forget(update: Update, context: CallbackContext) -> None:
    text = 'You can ask me to forget about you. I will be a bit sad but at least you data will be safely deleted from my database\n'
    text += 'To do so, please send me /forgetme\n'
    text += 'Please note that there is no coming back! You will have to start from scratch if you want to use me again\n'
    await update.message.reply_text(text)
    return

# forget me function
async def forget_me(update: Update, context: CallbackContext) -> None:
    database.delete_user(update.message.from_user.id)
    text = 'I have forgotten about you. I wish you the best!\n'
    text += 'If you want to use me again, please send /start\n'
    await update.message.reply_text(text)
    return

# qr data function
async def qr(update: Update, context: CallbackContext) -> None:
    if ' ' in update.message.text:
        _, input = update.message.text.split(' ', 1)
        await update.message.reply_photo(photo=qrcodes.qr_from_text(input))
    else:
        text = 'Please provide a text to generate a QRCode\n'
        text += 'Example : /qr example.com'
        await update.message.reply_text(text)
    return

# qr vcard function
async def qr_vcard(update: Update, context: CallbackContext) -> None:
    fields = ['First name', 'Last name', 'Phone number', 'Email address', 'Company name', 'Website URL']
    if ' ' in update.message.text:
        _, input = update.message.text.split('\n', 1)
        try:
            data = messages.retrieve_data(input)
            vcard_dict = {
                'fn': data['Last name'] + ',' + data['First name'],  # Nom complet
                'n': data['Last name']+';'+data['First name']+';;;',  # Nom
                'tel': data['Phone number'],  # Numéro de téléphone
                'email': data['Email address'],  # Adresse e-mail
                'org': data['Company name'],  # Nom de l'entreprise
                'url': data['Website URL']  # URL du site web
            }
            await update.message.reply_photo(photo=qrcodes.vcard_from_dict(vcard_dict=vcard_dict))
            return
        except Exception as e:
            print(e)
            text = 'Please make sure your input is correct and only add to the following template\n'
            text += 'For support, please see /help\n'
    else:
        text = 'Please copy and fill the following message to add the data for the Vcard generation\n'
    await update.message.reply_text(text)
    await update.message.reply_text(messages.prompt_data("/vcard", fields))
    return

# qr wifi function
async def qr_wifi(update: Update, context: CallbackContext):
    fields = ['WIFI Name', 'WIFI Password', 'WIFI Security (leave empty if you don\'t know)']
    if ' ' in update.message.text:
        _, input = update.message.text.split('\n', 1)
        try:
            data = messages.retrieve_data(input)
            ssid = data[fields[0]]
            password = data[fields[1]]
            security = data[fields[2]]
            if security == '':
                await update.message.reply_photo(photo=qrcodes.wifi_qr(ssid, password))
            else:
                await update.message.reply_photo(photo=qrcodes.wifi_qr(ssid, password, security))
            return
        except Exception as e:
            print(e)
            text = 'Please make sure your input is correct and only add to the following template\n'
            text += 'For support, please see /help\n'
    else:
        text = 'Please copy and fill the following message to add the data for the WIFI connection\n'
    await update.message.reply_text(text)
    await update.message.reply_text(messages.prompt_data("/wifi", fields))
    return

# gpt prompt
async def gpt(update: Update, context: CallbackContext) -> None:
    if ' ' in update.message.text:
        _, input = update.message.text.split(' ', 1)
        text = ia.prompt(input)
    else:
        text = 'Please provide a prompt to generate a text\n'
        text += 'Example : /gpt Tell me a story about a cat'
    await update.message.reply_text(text)
    return

# ics generation
async def ics(update: Update, context: CallbackContext) -> None:
    if ' ' in update.message.text:
        _, input = update.message.text.split(' ', 1)
        try:
            event_data = ia.extract_event(input)
            caption = 'Add me to your calendar!\n\n'
            caption += event_data['name']+'\n'
            caption += f"From {event_data['start']} to {event_data['end']}\n"
            document=mycalendar.create_event_ics(*event_data.values())
            await update.message.reply_document(caption=caption, document=document)
            return
        except Exception as e:
            print(e)
            text = 'Please tryy to give more info to help ia process you request\n'
            text += 'For support, please see /help\n'
    else:
        text = 'Please provide info to generate the ics file\n'
        text += 'Example : /ics breakfast tomorrow morning'
    await update.message.reply_text(text)
    return

# agep sticker generation
async def agep(update: Update, context: CallbackContext) -> None:
    if ' ' in update.message.text:
        _, input = update.message.text.split(' ', 1)
        image_bytes = stickergen.gen_sticker_agep(input)
        await update.message.reply_sticker(image_bytes)
    else:
        text = 'Please provide a text to generate a sticker\n'
        text += 'Example : /agep AGEPOUPOU'
        await update.message.reply_text(text)
    return

# Subscribe to periodic prompting
async def create_subscription(update: Update, context: CallbackContext) -> None:
    database.add_user(update.message.from_user.id, update.message.from_user.username, update.message.from_user.first_name)
    fields = ['Name', 'Description', 'Answers (separated by commas)']
    if ' ' in update.message.text:
        _, input = update.message.text.split('\n', 1)
        try:
            data = messages.retrieve_data(input)
            name = data[fields[0]]
            if database.subscription_exists(user_id=update.message.from_user.id, name=name):
                text = 'You already have a subscription with this name. Please copy your previous message, and send it again with a different name\n'
                await update.message.reply_text(text)
                return
            description = data[fields[1]]
            answers = data[fields[2]].split(',')
            sub = Subscription(update.message.from_user.id, name, description, answers)
            database.create_subscription(sub)
            markup = mytelegram.create_telegram_keyboard_frequency('freq', name, [Frequency.HOURLY, Frequency.DAILY])
            await update.message.reply_text('Choose you frequency', reply_markup=markup)
            return
        except Exception as e:
            print(e)
            text = 'Please make sure your input is correct and only add to the following template\n'
            text += 'For support, please see /help\n'
    else:
        text = 'Please copy and fill the following message to subscribe to a new data prompt\n'
    await update.message.reply_text(text)
    await update.message.reply_text(messages.prompt_data("/sub", fields))
    return

# Unsubscribe from periodic prompting
async def unsubscribe(update: Update, context: CallbackContext) -> None:
    if ' ' in update.message.text:
        _, input = update.message.text.split(' ', 1)
        sub = database.get_subscription_from_param(update.message.from_user.id, input)
        if database.subscription_exists(sub):
            database.update_subscription_state(sub, database.State.INACTIVE)
            text = 'You have been unsubscribed from '
        else:
            text = 'You are not subscribed to '
        text += input + '\n'
    else:
        text = 'Please provide the name of the subscription you want to unsubscribe from\n'
        text += 'Example : /unsub my_subscription'
    await update.message.reply_text(text)
    return

# Delete a periodic prompting
async def delete_subscription(update: Update, context: CallbackContext) -> None:
    if ' ' in update.message.text:
        _, input = update.message.text.split(' ', 1)
        sub = database.get_subscription_from_param(update.message.from_user.id, input)
        text = input + ' '
        if database.subscription_exists(sub):
            database.delete_subscription(sub)
            text += 'has been deleted\n'
        else:
            text += 'doesn\'t exist'
    else:
        text = 'Please provide the name of the subscription you want to delete\n'
        text += 'Example : /del my_subscription'
    await update.message.reply_text(text)
    return

# Handle callback query
async def handle_callback_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    function, data = query.data.split(SEPARATOR, 1)
    if function == 'freq':
        name, frequency = data.split(SEPARATOR)
        sub = database.get_subscription_from_param(update.callback_query.from_user.id, name)
        database.update_subscription_frequency(sub, frequency)
        database.update_subscription_state(sub, database.State.ACTIVE)
        await query.edit_message_text(text=f"You have been subscribed to {name} with frequency {frequency}")
    elif function == 'answer':
        name, timestamp, option = data.split(SEPARATOR)
        sub = database.get_subscription_from_param(update.callback_query.from_user.id, name)
        data = database.update_data(sub, datetime.now().date().isoformat(), option)
        # TODO change timestamp to keep the old one
        # TODO change method name
        markup = mytelegram.create_telegram_keyboard_from_list_with_timestamp('answer', sub.name, sub.answers, timestamp, data=data)
        await query.edit_message_reply_markup(reply_markup=markup)
    await query.answer()
    return

# Handle inline query
async def handle_inline_query(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    print(query)
    if not query:
        return
    
    results = []
    sticker = stickergen.gen_sticker_agep(query)
    sticker_message = await context.bot.send_sticker(chat_id=LOG_GROUP_ID, sticker=sticker)
    results.append(InlineQueryResultCachedSticker(
        id=str(uuid.uuid4()),
        sticker_file_id=sticker_message.sticker.file_id,
    ))
    await update.inline_query.answer(results, cache_time=0)
    return

# Auto subscriptions
async def auto_subscriptions() -> None:
    bot = telegram.Bot(token=TOKEN)
    subs: list[Subscription] = database.get_subscriptions_by_frequency(Frequency.DAILY)
    for sub in subs:
        text = f"<b>{sub.name}</b>!\n"
        text += f"{sub.description}\n"
        date = datetime.now().date().isoformat()
        markup = mytelegram.create_telegram_keyboard_from_list_with_timestamp('answer', sub.name, sub.answers, date, data=database.get_data(sub, date))
        await bot.send_message(chat_id=sub.user_id, text=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    return

# main function
def main() -> None:
    # Create application
    application = Application.builder().token(TOKEN).build()

    # General commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("forget", forget))
    application.add_handler(CommandHandler("forgetme", forget_me))
    # QR commands
    application.add_handler(CommandHandler("qr", qr))
    application.add_handler(CommandHandler("vcard", qr_vcard))
    application.add_handler(CommandHandler("wifi", qr_wifi))
    # IA commands
    application.add_handler(CommandHandler("ics", ics))
    application.add_handler(CommandHandler("gpt", gpt))
    # Stickers commands
    application.add_handler(CommandHandler("agep", agep))
    # Subscriptions commands
    application.add_handler(CommandHandler("subhelp", sub_help))
    application.add_handler(CommandHandler("sub", create_subscription))
    application.add_handler(CommandHandler("unsub", unsubscribe))
    application.add_handler(CommandHandler("del", delete_subscription))

    # When a button is pressed
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # When an inline query is made
    application.add_handler(InlineQueryHandler(handle_inline_query))

    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("function",
                        nargs='?',
                        help="The function to execute",
                        choices=["sub"])
    args = parser.parse_args()

    # If a function is specified, execute it and exit
    if args.function == "sub":
        asyncio.run(auto_subscriptions())
        return


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
    database.connect()
    main()
