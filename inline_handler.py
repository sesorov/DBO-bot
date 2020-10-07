import requests
import telegram
import json
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from setup import TOKEN, PROXY
from functions import calculate

import commands as cmd
from database import BankDatabase

CALLBACK_BUTTON_INDIVIDUAL = "callback_individual"
CALLBACK_BUTTON_ENTITY = "callback_entity"

CALLBACK_BUTTON_PRICE = "callback_primary_price"
CALLBACK_BUTTON_RELIABILITY = "callback_reliability"
CALLBACK_BUTTON_CONVENIENCE = "callback_convenience"
CALLBACK_BUTTON_DEPOSITS = "callback_deposits"
CALLBACK_BUTTON_INVESTMENTS = "callback_investments"
CALLBACK_BUTTON_DEPOSITS_INVESTMENTS = "callback_deposits_and_investments"
CALLBACK_BUTTON_ONLY_ACCOUNT = "callback_only_account"
CALLBACK_BUTTON_EXPENSES_CONTROL_YES = "callback_expense_yes"
CALLBACK_BUTTON_EXPENSES_CONTROL_NO = "callback_expense_no"

CALLBACK_BUTTON_NOTIFY_SMS = "callback_notify_sms"
CALLBACK_BUTTON_NOTIFY_SMS_EMAIL = "callback_notify_sms_email"
CALLBACK_BUTTON_NOTIFY_ALL = "callback_notify_all"
CALLBACK_BUTTON_NOTIFY_NONE = "callback_notify_none"
CALLBACK_BUTTON_SEND_MAIL_YES = "callback_send_mail_yes"
CALLBACK_BUTTON_SEND_MAIL_NO = "callback_send_mail_no"
CALLBACK_BUTTON_SALARY_REG_YES = "callback_salary_reg_yes"
CALLBACK_BUTTON_SALARY_REG_NO = "callback_salary_reg_no"
CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_YES = "callback_currency_transactions_yes"
CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_NO = "callback_currency_transactions_no"
CALLBACK_BUTTON_MULTICURRENCY_YES = "callback_multicurrency_yes"
CALLBACK_BUTTON_MULTICURRENCY_NO = "callback_multicurrency_no"
CALLBACK_BUTTON_PARTNER_NOTIFY_YES = "callback_partner_notify_yes"
CALLBACK_BUTTON_PARTNER_NOTIFY_NO = "callback_partner_notify_no"
CALLBACK_BUTTON_ALL_TYPES_ACC_YES = "callback_accounts_statements_yes"
CALLBACK_BUTTON_ALL_TYPES_ACC_NO = "callback_accounts_statements_no"

bot = Bot(
    token=TOKEN,
    # base_url=PROXY,  # delete it if connection via VPN
)

db_banks = BankDatabase()


class InlineKeyboardFactory:
    @staticmethod
    def get_individual_entity_keyboard() -> InlineKeyboardMarkup:
        """Get custom inline keyboard for choosing individual or entity bank db"""
        keyboard = [
            [
                InlineKeyboardButton("Физическое лицо", callback_data=CALLBACK_BUTTON_INDIVIDUAL)  # for individuals
            ],
            [
                InlineKeyboardButton("Юридическое лицо", callback_data=CALLBACK_BUTTON_ENTITY)
                # for organisations & companies
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_preferences_keyboard() -> InlineKeyboardMarkup:
        """Get custom inline keyboard for user preferences"""
        keyboard = [
            [
                InlineKeyboardButton("Цена", callback_data=CALLBACK_BUTTON_PRICE)  # the lower price is required
            ],
            [
                InlineKeyboardButton("Надёжность", callback_data=CALLBACK_BUTTON_RELIABILITY)
                # the most reliable bank is required
            ],
            [
                InlineKeyboardButton("Удобство", callback_data=CALLBACK_BUTTON_CONVENIENCE)
                # the most convenient bank is required
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_invest_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Вклады", callback_data=CALLBACK_BUTTON_DEPOSITS)
            ],
            [
                InlineKeyboardButton("Инвестиции", callback_data=CALLBACK_BUTTON_INVESTMENTS)
            ],
            [
                InlineKeyboardButton("И то, и другое", callback_data=CALLBACK_BUTTON_DEPOSITS_INVESTMENTS)
            ],
            [
                InlineKeyboardButton("Ничего из перечисленного", callback_data=CALLBACK_BUTTON_ONLY_ACCOUNT)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_expenses_control_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_EXPENSES_CONTROL_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_EXPENSES_CONTROL_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_sms_mail_push_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("SMS", callback_data=CALLBACK_BUTTON_NOTIFY_SMS)
            ],
            [
                InlineKeyboardButton("SMS + e-mail", callback_data=CALLBACK_BUTTON_NOTIFY_SMS_EMAIL)
            ],
            [
                InlineKeyboardButton("SMS + email + push", callback_data=CALLBACK_BUTTON_NOTIFY_ALL)
            ],
            [
                InlineKeyboardButton("Не важны", callback_data=CALLBACK_BUTTON_NOTIFY_NONE)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_send_mail_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_SEND_MAIL_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_SEND_MAIL_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_salary_registers_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_SALARY_REG_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_SALARY_REG_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_currency_transactions_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_multicurrency_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_MULTICURRENCY_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_MULTICURRENCY_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_partner_notification_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_PARTNER_NOTIFY_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_PARTNER_NOTIFY_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_all_types_of_accounts_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_ALL_TYPES_ACC_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_ALL_TYPES_ACC_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


class InlineCallback:

    @staticmethod
    def update_data(add_data: {}, file: json):
        try:
            with open(file, "r") as handle:
                data = json.load(handle)
            data.update(add_data)
        except FileNotFoundError:
            data = add_data
        with open(file, "w") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        return file, add_data

    @staticmethod
    def handle_keyboard_callback(update: Update, context=None):  # Gets callback_data from the pushed button
        query = update.callback_query  # Gets query from callback
        data = query.data  # callback_data of pushed button
        chat_id = update.effective_message.chat_id  # chat id for sending messages
        banks_individuals = db_banks.get_individuals()

        if data == CALLBACK_BUTTON_INDIVIDUAL:
            bot.send_message(chat_id=update.effective_message.chat_id,
                             text="Что для Вас важнее всего?",
                             reply_markup=InlineKeyboardFactory.get_preferences_keyboard())
            InlineCallback.update_data({"is_individual": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_INDIVIDUAL

        elif data == CALLBACK_BUTTON_ENTITY:
            bot.send_message(chat_id=update.effective_message.chat_id,
                             text="Вам необходимы SMS-, e-mail-, push-уведомления о движениях по счёту?",
                             reply_markup=InlineKeyboardFactory.get_sms_mail_push_keyboard())
            InlineCallback.update_data({"is_individual": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ENTITY

        elif data == CALLBACK_BUTTON_PRICE:  # ЦЕНА
            bot.send_message(chat_id=chat_id, text=f"Вы предпочитаете вклады или инвестиции?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_invest_keyboard())
            InlineCallback.update_data({"most_important": "price"}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_PRICE

        elif data == CALLBACK_BUTTON_RELIABILITY:  # НАДЁЖНОСТЬ
            bot.send_message(chat_id=chat_id, text=f"Вы предпочитаете вклады или инвестиции?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_invest_keyboard())
            InlineCallback.update_data({"most_important": "reliability"}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_RELIABILITY

        elif data == CALLBACK_BUTTON_CONVENIENCE:  # УДОБСТВО
            bot.send_message(chat_id=chat_id, text=f"Вы предпочитаете вклады или инвестиции?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_invest_keyboard())
            InlineCallback.update_data({"most_important": "convenience"}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_CONVENIENCE

        elif data == CALLBACK_BUTTON_DEPOSITS:
            bot.send_message(chat_id=chat_id, text=f"Вы желаете пользоваться контролем расходов?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_expenses_control_keyboard())
            InlineCallback.update_data({"deposits_investments_both_account": 0}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_DEPOSITS

        elif data == CALLBACK_BUTTON_INVESTMENTS:
            bot.send_message(chat_id=chat_id, text=f"Вы желаете пользоваться контролем расходов?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_expenses_control_keyboard())
            InlineCallback.update_data({"deposits_investments_both_account": 1}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_INVESTMENTS

        elif data == CALLBACK_BUTTON_DEPOSITS_INVESTMENTS:
            bot.send_message(chat_id=chat_id, text=f"Вы желаете пользоваться контролем расходов?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_expenses_control_keyboard())
            InlineCallback.update_data({"deposits_investments_both_account": 2}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_DEPOSITS_INVESTMENTS

        elif data == CALLBACK_BUTTON_ONLY_ACCOUNT:
            bot.send_message(chat_id=chat_id, text=f"Вы желаете пользоваться контролем расходов?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_expenses_control_keyboard())
            InlineCallback.update_data({"deposits_investments_both_account": 3}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ONLY_ACCOUNT

        elif data == CALLBACK_BUTTON_EXPENSES_CONTROL_YES:
            InlineCallback.update_data({"is_expenses_control": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_EXPENSES_CONTROL_YES

        elif data == CALLBACK_BUTTON_EXPENSES_CONTROL_NO:
            InlineCallback.update_data({"is_expenses_control": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_EXPENSES_CONTROL_NO

        # Only entity

        elif data == CALLBACK_BUTTON_NOTIFY_SMS:
            bot.send_message(chat_id=chat_id, text=f"Вас интересует возможность отправки писем в банк из системы ДБО?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_send_mail_keyboard())
            InlineCallback.update_data({"notify": 1}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NOTIFY_SMS

        elif data == CALLBACK_BUTTON_NOTIFY_SMS_EMAIL:
            bot.send_message(chat_id=chat_id, text=f"Вас интересует возможность отправки писем в банк из системы ДБО?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_send_mail_keyboard())
            InlineCallback.update_data({"notify": 2}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NOTIFY_SMS_EMAIL

        elif data == CALLBACK_BUTTON_NOTIFY_ALL:
            bot.send_message(chat_id=chat_id, text=f"Вас интересует возможность отправки писем в банк из системы ДБО?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_send_mail_keyboard())
            InlineCallback.update_data({"notify": 3}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NOTIFY_ALL

        elif data == CALLBACK_BUTTON_NOTIFY_NONE:
            bot.send_message(chat_id=chat_id, text=f"Вас интересует возможность отправки писем в банк из системы ДБО?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_send_mail_keyboard())
            InlineCallback.update_data({"notify": 0}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NOTIFY_NONE

        elif data == CALLBACK_BUTTON_SEND_MAIL_YES:
            bot.send_message(chat_id=chat_id, text=f"Вам важна возможность отправки реестров на заработную плату?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_salary_registers_keyboard())
            InlineCallback.update_data({"send_mail": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_SEND_MAIL_YES

        elif data == CALLBACK_BUTTON_SEND_MAIL_NO:
            bot.send_message(chat_id=chat_id, text=f"Вам важна возможность отправки реестров на заработную плату?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_salary_registers_keyboard())
            InlineCallback.update_data({"send_mail": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_SEND_MAIL_NO

        elif data == CALLBACK_BUTTON_SALARY_REG_YES:
            bot.send_message(chat_id=chat_id, text=f"Должна ли система ДБО формировать сведения о валютных операциях?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_currency_transactions_keyboard())
            InlineCallback.update_data({"salary_registers": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_SALARY_REG_YES

        elif data == CALLBACK_BUTTON_SALARY_REG_NO:
            bot.send_message(chat_id=chat_id, text=f"Должна ли система ДБО формировать сведения о валютных операциях?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_currency_transactions_keyboard())
            InlineCallback.update_data({"salary_registers": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_SALARY_REG_NO

        elif data == CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_YES:
            bot.send_message(chat_id=chat_id, text=f"Требуется ли вам поддержка мультивалютных платежей?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_multicurrency_keyboard())
            InlineCallback.update_data({"form_currency_transactions": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_YES

        elif data == CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_NO:
            bot.send_message(chat_id=chat_id, text=f"Требуется ли вам поддержка мультивалютных платежей?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_multicurrency_keyboard())
            InlineCallback.update_data({"form_currency_transactions": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_NO

        elif data == CALLBACK_BUTTON_MULTICURRENCY_YES:
            bot.send_message(chat_id=chat_id, text=f"Важно ли вам уведомлять партнёров о платежах в системе ДБО?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_partner_notification_keyboard())
            InlineCallback.update_data({"is_multicurrency": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_MULTICURRENCY_YES

        elif data == CALLBACK_BUTTON_MULTICURRENCY_NO:
            bot.send_message(chat_id=chat_id, text=f"Важно ли вам уведомлять партнёров о платежах в системе ДБО?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_partner_notification_keyboard())
            InlineCallback.update_data({"is_multicurrency": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_MULTICURRENCY_NO

        elif data == CALLBACK_BUTTON_PARTNER_NOTIFY_YES:
            bot.send_message(chat_id=chat_id, text=f"Вы желаете получать все виды счетов и выписок?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_all_types_of_accounts_keyboard())
            InlineCallback.update_data({"notify_partner": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_PARTNER_NOTIFY_YES

        elif data == CALLBACK_BUTTON_PARTNER_NOTIFY_NO:
            bot.send_message(chat_id=chat_id, text=f"Вы желаете получать все виды счетов и выписок?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_all_types_of_accounts_keyboard())
            InlineCallback.update_data({"notify_partner": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_PARTNER_NOTIFY_NO

        elif data == CALLBACK_BUTTON_ALL_TYPES_ACC_YES:
            bot.send_message(chat_id=chat_id, text=f"Спасибо за уделённое время, подводим итог...")
            InlineCallback.update_data({"get_all_types_acc": True}, f"personal/personal_{chat_id}.json")
            calculate(chat_id=chat_id)
            return CALLBACK_BUTTON_ALL_TYPES_ACC_YES

        elif data == CALLBACK_BUTTON_ALL_TYPES_ACC_NO:
            bot.send_message(chat_id=chat_id, text=f"Спасибо за уделённое время, подводим итог...")
            InlineCallback.update_data({"get_all_types_acc": False}, f"personal/personal_{chat_id}.json")
            calculate(chat_id=chat_id)
            return CALLBACK_BUTTON_ALL_TYPES_ACC_NO
