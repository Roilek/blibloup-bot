from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from . import database
from models.enumerations import Frequency

SEPARATOR = "#"

def create_telegram_keyboard(buttons: list[str]) -> InlineKeyboardMarkup:
    """Returns a telegram keyboard"""
    keyboard = [[InlineKeyboardButton(text, callback_data=text) for text in buttons]]
    return InlineKeyboardMarkup(keyboard)

# Create Telegram keyboard for choosing a frequency for a subscription
def create_telegram_keyboard_frequency(function_name: str, name: str, frequencies: list[Frequency]) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(f.value, callback_data=SEPARATOR.join([function_name, name, f.value]))] for f in frequencies]
    return InlineKeyboardMarkup(keyboard)

# Create Telegram keyboard from list of items
def create_telegram_keyboard_from_list(function_name: str, name: str, items: list[str], timestamp = None, chosen: str = None, col: int = 1) -> InlineKeyboardMarkup:
    # create the keyboard according to the number of columns
    if col == 1:
        keyboard = [[InlineKeyboardButton(("✅ " if chosen == item else "") + item, callback_data=SEPARATOR.join([function_name, name, item]))] for item in items]
    else:
        keyboard = [[InlineKeyboardButton(("✅ " if chosen == item else "") + item, callback_data=SEPARATOR.join([function_name, name, item])) for item in items[i:i + col]] for i in range(0, len(items), col)]
    return InlineKeyboardMarkup(keyboard)

# Create Telegram keyboard with a function identifier and the name of the subscription
def create_telegram_keyboard_from_list_with_timestamp(function_name: str, name: str, items: list[str], timestamp: str, data: list[str]) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(("✅ " if item in data else "") + item, callback_data=SEPARATOR.join([function_name, name, timestamp, item])) for item in items]]
    return InlineKeyboardMarkup(keyboard)
    