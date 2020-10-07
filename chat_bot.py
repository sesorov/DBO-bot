#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import commands as cmd

from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

from inline_handler import InlineCallback

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    actions_keyboard = [["Брокер ДБО"], ["Помощь"]]
    update.message.reply_text(f'Здравствуйте, {update.effective_user.first_name}! Пожалуйста, выберите действие.',
                              reply_markup=ReplyKeyboardMarkup(actions_keyboard, one_time_keyboard=True))


def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введите команду /start для начала. ')


def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    # bot = Bot(
    #     token=TOKEN,
    #     base_url=PROXY,  # delete it if connection via VPN
    # )
    # updater = Updater(bot=bot, use_context=True)

    # Connect via socks proxy
    REQUEST_KWARGS = {
        'proxy_url': PROXY,
        # Optional, if you need authentication:
        # 'urllib3_proxy_kwargs': {
        #     'username': 'name',
        #     'password': 'passwd',
        # }
    }

    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('tst', cmd.command_closest_bank))
    updater.dispatcher.add_handler(CommandHandler('dbo', cmd.command_dbo_main))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^(Брокер ДБО)$'), cmd.command_dbo_main))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^(Помощь)$'), chat_help))

    # location handler
    updater.dispatcher.add_handler(MessageHandler(Filters.location, cmd.get_location))

    # inline handler
    updater.dispatcher.add_handler(CallbackQueryHandler(callback=InlineCallback.handle_keyboard_callback))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    main()
