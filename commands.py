import json

from telegram import Update, ParseMode, Bot, ChatAction, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import CallbackContext
from setup import TOKEN
from database import BankDatabase

from inline_handler import InlineKeyboardFactory

bot = Bot(
    token=TOKEN,
    # base_url=PROXY,  # delete it if connection via VPN
)

db_banks = BankDatabase()


def get_location(update: Update, context: CallbackContext):
    """Get user's location"""
    location = f"{update.message.location.latitude}, {update.message.location.longitude}"
    with open(f"personal/personal_{update.message.chat.id}.json", 'w+') as handle:
        json.dump({"location": location}, handle, ensure_ascii=False, indent=2)
    bot.send_message(chat_id=update.message.chat_id, text="Got your location!", reply_markup=ReplyKeyboardRemove())


def command_closest_bank(update: Update, context: CallbackContext):
    location_button = KeyboardButton('Send my location', request_location=True)
    keyboard = ReplyKeyboardMarkup([[location_button]])
    bot.send_message(chat_id=update.message.chat_id, text="Firstly, let's figure out where are you from...",
                     reply_markup=keyboard)


def command_dbo_main(update: Update, context: CallbackContext):
    bot.send_message(chat_id=update.effective_message.chat_id,
                     text="Давайте определимся с вашим статусом. Вы:",
                     reply_markup=InlineKeyboardFactory.get_individual_entity_keyboard())
