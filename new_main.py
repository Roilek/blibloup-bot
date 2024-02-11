""" 
Create a python Telegram bot that hosts multiple functionnalities : 
- Stickers generation with specific text and font
- QRCodes generation for text, URL, VCard, WIFI
- Chatbot that can answer to basic questions
- ICS files generation for events, based on natural language input
- Subscribe to various functionnalities like :
    - Receiving updates on webpage changes
    - Receiving notifications priodically to input data like the time the user slept

Most of the functionnalities should also be available inline, so that the user can use them in any chat.
"""

from dotenv import load_dotenv
import os
import asyncio
import argparse

import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler, CallbackContext

from new_helpers import qrcodes, messages, mycalendar, ia

load_dotenv()

TOKEN = os.getenv('TOKEN')
PORT = int(os.getenv('PORT', 5000))
HEROKU_PATH = os.getenv('HEROKU_PATH')

# start function
async def start(update: Update, context: CallbackContext) -> None:
    text = 'Hey there! I\'m Blibloup bot and I can do a loooooot of things! \n'
    text += 'Send me /help to see all the things I can do! \n'
    await update.message.reply_text(text)
    return


# help function
async def help_command(update: Update, context: CallbackContext) -> None:
    text = 'Here are the things I can do : \n'
    text += '/start : Start the bot \n'
    text += '/help: Show this message \n'
    text += '/qr [text] : Generate a QRCode for text, url\n'
    text += '/vcard : Generate a QRCode for contact info\n'
    text += '/wifi : Generate a QRCode for wifi connection\n'
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
        except Exception as e:
            print(e)
            text = 'Please make sure your input is correct and only add to the following template\n'
            text += 'For support, please see /help\n'
            await update.message.reply_text(text)
            await update.message.reply_text(messages.prompt_data("/vcard", fields))
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
        except Exception as e:
            print(e)
            text = 'Please make sure your input is correct and only add to the following template\n'
            text += 'For support, please see /help\n'
            await update.message.reply_text(text)
            await update.message.reply_text(messages.prompt_data("/wifi", fields))
    else:
        text = 'Please copy and fill the following message to add the data for the WIFI connection\n'
        await update.message.reply_text(text)
        await update.message.reply_text(messages.prompt_data("/wifi", fields))
    return

# ics generation
async def ics(update: Update, context: CallbackContext) -> None:
    if ' ' in update.message.text:
        _, input = update.message.text.split(' ', 1)
        event_data = ia.extract_event(input)
        caption = 'Add me to your calendar!\n\n'
        caption += event_data['name']+'\n'
        caption += f"From {event_data['start']} to {event_data['end']}\n"
        document=mycalendar.create_event_ics(*event_data.values())
        await update.message.reply_document(caption=caption, document=document)
    else:
        text = 'Please provide info to generate the ics file\n'
        text += 'Example : /ics breakfast tomorrow morning'
        await update.message.reply_text(text)
    return


def main() -> None:
    # Create application
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("qr", qr))
    application.add_handler(CommandHandler("vcard", qr_vcard))
    application.add_handler(CommandHandler("wifi", qr_wifi))
    application.add_handler(CommandHandler("ics", ics))

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
