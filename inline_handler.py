import requests
import telegram
import json
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from setup import TOKEN, PROXY
from functions import calculate
from database import BankDatabase

CALLBACK_BUTTON_SIMPLE = "callback_dbo_simple"
CALLBACK_BUTTON_STANDARD = "callback_dbo_standard"

CALLBACK_BUTTON_INDIVIDUAL = "callback_individual"
CALLBACK_BUTTON_ENTITY = "callback_entity"

# individuals
CALLBACK_BUTTON_PRICE = "callback_primary_price"
CALLBACK_BUTTON_RELIABILITY = "callback_reliability"
CALLBACK_BUTTON_CONVENIENCE = "callback_convenience"
CALLBACK_BUTTON_DEPOSITS = "callback_deposits"
CALLBACK_BUTTON_INVESTMENTS = "callback_investments"
CALLBACK_BUTTON_DEPOSITS_INVESTMENTS = "callback_deposits_and_investments"
CALLBACK_BUTTON_ONLY_ACCOUNT = "callback_only_account"

CALLBACK_BUTTON_EXPENSES_CONTROL_YES = "callback_expense_yes"
CALLBACK_BUTTON_EXPENSES_CONTROL_NO = "callback_expense_no"

CALLBACK_BUTTON_GPAY_YES = "callback_gpay_yes"
CALLBACK_BUTTON_GPAY_NO = "callback_gpay_no"
CALLBACK_BUTTON_VISA = "callback_visa"
CALLBACK_BUTTON_MASTERCARD = "callback_mastercard"
CALLBACK_BUTTON_VISA_MASTERCARD = "callback_visa_mastercard"
CALLBACK_BUTTON_NO_VISA_MC = "callback_no_visa_mastercard"

CALLBACK_BUTTON_HELP_PHONE = "callback_help_phone"
CALLBACK_BUTTON_HELP_EMAIL = "callback_help_email"
CALLBACK_BUTTON_HELP_VK = "callback_help_social_networks"
CALLBACK_BUTTON_HELP_CHAT_HUMAN = "callback_help_chat_human"
CALLBACK_BUTTON_HELP_CHAT_BOT = "callback_help_chat_bot"
CALLBACK_BUTTON_HELP_NEXT = "callback_help_next"

CALLBACK_BUTTON_INDIVIDUAL_0_50 = "callback_individual_0_50"
CALLBACK_BUTTON_INDIVIDUAL_0_150 = "callback_individual_0_150"
CALLBACK_BUTTON_INDIVIDUAL_150_2000 = "callback_individual_150_2000"
CALLBACK_BUTTON_INDIVIDUAL_2000_10000 = "callback_individual_2000_10000"
CALLBACK_BUTTON_INDIVIDUAL_10000_MORE = "callback_individual_10000_more"
CALLBACK_BUTTON_INDIVIDUAL_ANY_COST = "callback_individual_any_cost"

CALLBACK_BUTTON_SMS_BANK_YES = "callback_sms_bank_yes"
CALLBACK_BUTTON_SMS_BANK_NO = "callback_sms_bank_no"

# entities
CALLBACK_BUTTON_NOTIFY_SMS = "callback_notify_sms"
CALLBACK_BUTTON_NOTIFY_SMS_EMAIL = "callback_notify_sms_email"
CALLBACK_BUTTON_NOTIFY_ALL = "callback_notify_all"
CALLBACK_BUTTON_NOTIFY_NONE = "callback_notify_none"

CALLBACK_BUTTON_SEND_MAIL_YES = "callback_send_mail_yes"
CALLBACK_BUTTON_SEND_MAIL_NO = "callback_send_mail_no"
CALLBACK_BUTTON_SALARY_REG_YES = "callback_salary_reg_yes"
CALLBACK_BUTTON_SALARY_REG_NO = "callback_salary_reg_no"

CALLBACK_BUTTON_SIMPLE_CURRENCY_YES = "callback_simple_currency_yes"
CALLBACK_BUTTON_SIMPLE_CURRENCY_NO = "callback_simple_currency_no"
CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_YES = "callback_currency_transactions_yes"
CALLBACK_BUTTON_CURRENCY_TRANSACTIONS_NO = "callback_currency_transactions_no"
CALLBACK_BUTTON_MULTICURRENCY_YES = "callback_multicurrency_yes"
CALLBACK_BUTTON_MULTICURRENCY_NO = "callback_multicurrency_no"

CALLBACK_BUTTON_ENTITY_3000 = "callback_entity_cost_3000"
CALLBACK_BUTTON_ENTITY_6000 = "callback_entity_cost_6000"
CALLBACK_BUTTON_ENTITY_10000 = "callback_entity_cost_10000"
CALLBACK_BUTTON_ENTITY_ANY_COST = "callback_entity_cost_any"

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
    def get_dbo_mode_keyboard() -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton("Упрощённый", callback_data=CALLBACK_BUTTON_SIMPLE)
            ],
            [
                InlineKeyboardButton("Стандартный", callback_data=CALLBACK_BUTTON_STANDARD)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

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

    @staticmethod
    def get_gpay_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_GPAY_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_GPAY_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_visa_mc_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("VISA", callback_data=CALLBACK_BUTTON_VISA)
            ],
            [
                InlineKeyboardButton("MasterCard", callback_data=CALLBACK_BUTTON_MASTERCARD)
            ],
            [
                InlineKeyboardButton("Обе", callback_data=CALLBACK_BUTTON_VISA_MASTERCARD)
            ],
            [
                InlineKeyboardButton("Другая платёжная система (напр. МИР)", callback_data=CALLBACK_BUTTON_NO_VISA_MC)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_help_keyboard(is_phone=False, is_email=False, is_vk=False, is_chat_h=False, is_chat_bot=False):
        keyboard = [
            [
                InlineKeyboardButton(f"Телефон {'✅' if is_phone else ''}", callback_data=CALLBACK_BUTTON_HELP_PHONE)
                # ✅
            ],
            [
                InlineKeyboardButton(f"e-mail {'✅' if is_email else ''}", callback_data=CALLBACK_BUTTON_HELP_EMAIL)
            ],
            [
                InlineKeyboardButton(f"Социальные сети {'✅' if is_vk else ''}",
                                     callback_data=CALLBACK_BUTTON_HELP_VK)
            ],
            [
                InlineKeyboardButton(f"Чат с оператором {'✅' if is_chat_h else ''}",
                                     callback_data=CALLBACK_BUTTON_HELP_CHAT_HUMAN)
            ],
            [
                InlineKeyboardButton(f"Чат-бот {'✅' if is_chat_bot else ''}",
                                     callback_data=CALLBACK_BUTTON_HELP_CHAT_BOT)
            ],
            [
                InlineKeyboardButton(f"Я выбрал нужные варианты ->", callback_data=CALLBACK_BUTTON_HELP_NEXT)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_mobile_pc_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Мобильные устройства", callback_data=CALLBACK_BUTTON_NOTIFY_ALL)
            ],
            [
                InlineKeyboardButton("ПК", callback_data=CALLBACK_BUTTON_NOTIFY_SMS_EMAIL)
            ],
            [
                InlineKeyboardButton("Оба варианта / Неважно / Неизвестно",
                                     callback_data=CALLBACK_BUTTON_NOTIFY_NONE)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_simple_currency_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_SIMPLE_CURRENCY_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_SIMPLE_CURRENCY_NO)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_entity_price_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("До 3.000 руб в месяц", callback_data=CALLBACK_BUTTON_ENTITY_3000)
            ],
            [
                InlineKeyboardButton("До 6.000 руб в месяц", callback_data=CALLBACK_BUTTON_ENTITY_6000)
            ],
            [
                InlineKeyboardButton("До 10.000 руб в месяц", callback_data=CALLBACK_BUTTON_ENTITY_10000)
            ],
            [
                InlineKeyboardButton("Любая", callback_data=CALLBACK_BUTTON_ENTITY_ANY_COST)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_standard_individual_price_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Бесплатная | До 50 р/мес", callback_data=CALLBACK_BUTTON_INDIVIDUAL_0_50)
            ],
            [
                InlineKeyboardButton("От 0 до 150 р/мес", callback_data=CALLBACK_BUTTON_INDIVIDUAL_0_150)
            ],
            [
                InlineKeyboardButton("От 150 до 2000 р/мес", callback_data=CALLBACK_BUTTON_INDIVIDUAL_150_2000)
            ],
            [
                InlineKeyboardButton("От 2000 до 10000 р/мес", callback_data=CALLBACK_BUTTON_INDIVIDUAL_2000_10000)
            ],
            [
                InlineKeyboardButton("От 10000 р/мес (Премиум)", callback_data=CALLBACK_BUTTON_INDIVIDUAL_10000_MORE)
            ],
            [
                InlineKeyboardButton("Не важна / учитывать любую", callback_data=CALLBACK_BUTTON_INDIVIDUAL_ANY_COST)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_sms_banking_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data=CALLBACK_BUTTON_SMS_BANK_YES)
            ],
            [
                InlineKeyboardButton("Нет", callback_data=CALLBACK_BUTTON_SMS_BANK_NO)
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
        except OSError:
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
        is_simple = False
        try:
            with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
                if json.load(handle).get("is_simple"):
                    is_simple = True
                else:
                    is_simple = False
        except OSError:
            pass

        if data == CALLBACK_BUTTON_SIMPLE:
            bot.send_message(chat_id=update.effective_message.chat_id,
                             text="Давайте определимся с вашим статусом. Вы:",
                             reply_markup=InlineKeyboardFactory.get_individual_entity_keyboard())
            InlineCallback.update_data({"is_simple": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_SIMPLE

        elif data == CALLBACK_BUTTON_STANDARD:
            bot.send_message(chat_id=update.effective_message.chat_id,
                             text="Давайте определимся с вашим статусом. Вы:",
                             reply_markup=InlineKeyboardFactory.get_individual_entity_keyboard())
            InlineCallback.update_data({"is_simple": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_STANDARD

        elif data == CALLBACK_BUTTON_INDIVIDUAL:
            with open(f"personal/personal_{chat_id}.json") as handle:
                if json.load(handle)['is_simple']:
                    bot.send_message(chat_id=update.effective_message.chat_id,
                                     text="Что для Вас важнее всего?",
                                     reply_markup=InlineKeyboardFactory.get_preferences_keyboard())
                else:
                    bot.send_message(chat_id=chat_id, text=f"Какой способ связи с банком вы предпочитаете?",
                                     parse_mode=telegram.ParseMode.HTML,
                                     reply_markup=InlineKeyboardFactory.get_help_keyboard())
                    InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
                    InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
                    InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
                    InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
                    InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_individual": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_INDIVIDUAL

        elif data == CALLBACK_BUTTON_ENTITY:
            if is_simple:
                bot.send_message(chat_id=update.effective_message.chat_id,
                                 text="Ваша компания будет взаимодействовать с ДБО преимущественно с мобильных устройств или ПК?",
                                 reply_markup=InlineKeyboardFactory.get_mobile_pc_keyboard())
                InlineCallback.update_data({"is_individual": False}, f"personal/personal_{chat_id}.json")
            else:
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
            bot.send_message(chat_id=chat_id, text=f"Вы используете Google Pay?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_gpay_keyboard())
            InlineCallback.update_data({"is_expenses_control": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_EXPENSES_CONTROL_YES

        elif data == CALLBACK_BUTTON_EXPENSES_CONTROL_NO:
            bot.send_message(chat_id=chat_id, text=f"Вы используете Google Pay?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_gpay_keyboard())
            InlineCallback.update_data({"is_expenses_control": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_EXPENSES_CONTROL_NO

        elif data == CALLBACK_BUTTON_GPAY_YES:
            InlineCallback.update_data({"is_gpay": True}, f"personal/personal_{chat_id}.json")
            if is_simple:
                bot.send_message(chat_id=chat_id, text=f"Какой способ связи с банком вы предпочитаете?",
                                       parse_mode=telegram.ParseMode.HTML,
                                       reply_markup=InlineKeyboardFactory.get_help_keyboard())
                InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")
            else:
                bot.send_message(chat_id=chat_id, text=f"Вы используете VISA или Mastercard?",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_visa_mc_keyboard())
            return CALLBACK_BUTTON_GPAY_YES

        elif data == CALLBACK_BUTTON_GPAY_NO:
            InlineCallback.update_data({"is_gpay": False}, f"personal/personal_{chat_id}.json")
            if is_simple:
                bot.send_message(chat_id=chat_id, text=f"Какой способ связи с банком вы предпочитаете?",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_help_keyboard())
                InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
                InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")

            else:
                bot.send_message(chat_id=chat_id, text=f"Выберите ограничение по стоимости ДБО:",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_standard_individual_price_keyboard())
            return CALLBACK_BUTTON_GPAY_NO

        elif data == CALLBACK_BUTTON_VISA:
            bot.send_message(chat_id=chat_id, text=f"Выберите ограничение по стоимости ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_standard_individual_price_keyboard())
            InlineCallback.update_data({"is_visa": True}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_mastercard": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_VISA

        elif data == CALLBACK_BUTTON_MASTERCARD:
            bot.send_message(chat_id=chat_id, text=f"Выберите ограничение по стоимости ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_standard_individual_price_keyboard())
            InlineCallback.update_data({"is_visa": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_mastercard": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_MASTERCARD

        elif data == CALLBACK_BUTTON_VISA_MASTERCARD:
            bot.send_message(chat_id=chat_id, text=f"Выберите ограничение по стоимости ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_standard_individual_price_keyboard())
            InlineCallback.update_data({"is_visa": True}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_mastercard": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_VISA_MASTERCARD

        elif data == CALLBACK_BUTTON_NO_VISA_MC:
            bot.send_message(chat_id=chat_id, text=f"Выберите ограничение по стоимости ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_standard_individual_price_keyboard())
            InlineCallback.update_data({"is_visa": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_mastercard": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NO_VISA_MC

        elif data == CALLBACK_BUTTON_HELP_PHONE or data == CALLBACK_BUTTON_HELP_EMAIL \
                or data == CALLBACK_BUTTON_HELP_VK or data == CALLBACK_BUTTON_HELP_CHAT_HUMAN or data == CALLBACK_BUTTON_HELP_CHAT_BOT:
            with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
                personal = json.load(handle)
                if data == CALLBACK_BUTTON_HELP_PHONE:
                    if not personal['is_help_phone']:
                        InlineCallback.update_data({"is_help_phone": True}, f"personal/personal_{chat_id}.json")
                    else:
                        InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
                elif data == CALLBACK_BUTTON_HELP_EMAIL:
                    if not personal['is_help_email']:
                        InlineCallback.update_data({"is_help_email": True}, f"personal/personal_{chat_id}.json")
                    else:
                        InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
                elif data == CALLBACK_BUTTON_HELP_VK:
                    if not personal['is_help_vk']:
                        InlineCallback.update_data({"is_help_vk": True}, f"personal/personal_{chat_id}.json")
                    else:
                        InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
                elif data == CALLBACK_BUTTON_HELP_CHAT_HUMAN:
                    if not personal['is_help_chat_human']:
                        InlineCallback.update_data({"is_help_chat_human": True}, f"personal/personal_{chat_id}.json")
                    else:
                        InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
                elif data == CALLBACK_BUTTON_HELP_CHAT_BOT:
                    if not personal['is_help_chat_bot']:
                        InlineCallback.update_data({"is_help_chat_bot": True}, f"personal/personal_{chat_id}.json")
                    else:
                        InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")
            with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
                personal = json.load(handle)
                tmp = bot.send_message(text=f"Какой способ связи с банком вы предпочитаете?", chat_id=chat_id,
                                       reply_markup=InlineKeyboardFactory.get_help_keyboard(
                                           is_phone=personal['is_help_phone'],
                                           is_email=personal['is_help_email'],
                                           is_vk=personal['is_help_vk'],
                                           is_chat_h=personal['is_help_chat_human'],
                                           is_chat_bot=personal['is_help_chat_bot']))
                bot.delete_message(chat_id=chat_id, message_id=tmp.message_id - 1)

        elif data == CALLBACK_BUTTON_HELP_NEXT:
            if is_simple:
                with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
                    personal = json.load(handle)
                    if personal['is_individual']:
                        bot.send_message(chat_id=chat_id, text=f"Желаете учитывать стоимость СМС-банкинга?",
                                         parse_mode=telegram.ParseMode.HTML,
                                         reply_markup=InlineKeyboardFactory.get_sms_banking_keyboard())
                    else:
                        bot.send_message(chat_id=chat_id, text=f"Спасибо за уделённое время, подводим итог...")
                        calculate(chat_id=chat_id)
            else:
                with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
                    personal = json.load(handle)
                    if personal['is_individual']:
                        bot.send_message(chat_id=chat_id, text=f"Вы предпочитаете вклады или инвестиции?",
                                         parse_mode=telegram.ParseMode.HTML,
                                         reply_markup=InlineKeyboardFactory.get_invest_keyboard())
                    else:
                        bot.send_message(chat_id=chat_id, text=f"Спасибо за уделённое время, подводим итог...")
                        calculate(chat_id=chat_id)
            return CALLBACK_BUTTON_HELP_NEXT

        elif data == CALLBACK_BUTTON_INDIVIDUAL_0_50:
            InlineCallback.update_data({"min price": 0}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 50}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Желаете учитывать стоимость СМС-банкинга?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_sms_banking_keyboard())
            return CALLBACK_BUTTON_INDIVIDUAL_0_50

        elif data == CALLBACK_BUTTON_INDIVIDUAL_0_150:
            InlineCallback.update_data({"min price": 0}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 150}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Желаете учитывать стоимость СМС-банкинга?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_sms_banking_keyboard())
            return CALLBACK_BUTTON_INDIVIDUAL_0_150

        elif data == CALLBACK_BUTTON_INDIVIDUAL_150_2000:
            InlineCallback.update_data({"min price": 150}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 2000}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Желаете учитывать стоимость СМС-банкинга?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_sms_banking_keyboard())
            return CALLBACK_BUTTON_INDIVIDUAL_150_2000

        elif data == CALLBACK_BUTTON_INDIVIDUAL_2000_10000:
            InlineCallback.update_data({"min price": 2000}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 10000}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Желаете учитывать стоимость СМС-банкинга?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_sms_banking_keyboard())
            return CALLBACK_BUTTON_INDIVIDUAL_2000_10000

        elif data == CALLBACK_BUTTON_INDIVIDUAL_10000_MORE:
            InlineCallback.update_data({"min price": 10000}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 999999999}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Желаете учитывать стоимость СМС-банкинга?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_sms_banking_keyboard())
            return CALLBACK_BUTTON_INDIVIDUAL_10000_MORE

        elif data == CALLBACK_BUTTON_INDIVIDUAL_ANY_COST:
            InlineCallback.update_data({"min price": 0}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 999999999}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Желаете учитывать стоимость СМС-банкинга?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_sms_banking_keyboard())
            return CALLBACK_BUTTON_INDIVIDUAL_ANY_COST

        elif data == CALLBACK_BUTTON_SMS_BANK_YES:
            InlineCallback.update_data({"sms": True}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Спасибо за уделённое время, подводим итог...")
            calculate(chat_id=chat_id)
            return CALLBACK_BUTTON_SMS_BANK_YES

        elif data == CALLBACK_BUTTON_SMS_BANK_NO:
            InlineCallback.update_data({"sms": False}, f"personal/personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text=f"Спасибо за уделённое время, подводим итог...")
            calculate(chat_id=chat_id)
            return CALLBACK_BUTTON_SMS_BANK_NO

        # Only entity

        elif data == CALLBACK_BUTTON_NOTIFY_SMS:
            bot.send_message(chat_id=chat_id,
                             text=f"Вас интересует возможность отправки писем, заверенных электронной подписью, в банк из системы ДБО?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_send_mail_keyboard())
            InlineCallback.update_data({"notify": 1}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NOTIFY_SMS

        elif data == CALLBACK_BUTTON_NOTIFY_SMS_EMAIL:
            if is_simple:
                bot.send_message(chat_id=chat_id,
                                 text=f"Ваша компания будет оперировать с валютой через ДБО?",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_simple_currency_keyboard())
            else:
                bot.send_message(chat_id=chat_id,
                                 text=f"Вас интересует возможность отправки писем, заверенных электронной подписью, в банк из системы ДБО?",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_send_mail_keyboard())
            InlineCallback.update_data({"notify": 2}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NOTIFY_SMS_EMAIL

        elif data == CALLBACK_BUTTON_NOTIFY_ALL:
            if is_simple:
                bot.send_message(chat_id=chat_id,
                                 text=f"Ваша компания будет оперировать с валютой через ДБО?",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_simple_currency_keyboard())
            else:
                bot.send_message(chat_id=chat_id,
                                 text=f"Вас интересует возможность отправки писем в банк из системы ДБО?",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_send_mail_keyboard())
            InlineCallback.update_data({"notify": 3}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_NOTIFY_ALL

        elif data == CALLBACK_BUTTON_NOTIFY_NONE:
            if is_simple:
                bot.send_message(chat_id=chat_id,
                                 text=f"Ваша компания будет оперировать с валютой через ДБО?",
                                 parse_mode=telegram.ParseMode.HTML,
                                 reply_markup=InlineKeyboardFactory.get_simple_currency_keyboard())
            else:
                bot.send_message(chat_id=chat_id,
                                 text=f"Вас интересует возможность отправки писем в банк из системы ДБО?",
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

        elif data == CALLBACK_BUTTON_SIMPLE_CURRENCY_YES:
            bot.send_message(chat_id=chat_id, text=f"Выберите приемлемую стоимость услуг ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_entity_price_keyboard())
            InlineCallback.update_data({"using_currency": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_SIMPLE_CURRENCY_YES

        elif data == CALLBACK_BUTTON_SIMPLE_CURRENCY_NO:
            bot.send_message(chat_id=chat_id, text=f"Выберите приемлемую стоимость услуг ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_entity_price_keyboard())
            InlineCallback.update_data({"using_currency": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_SIMPLE_CURRENCY_NO

        elif data == CALLBACK_BUTTON_ENTITY_3000:
            bot.send_message(chat_id=chat_id, text=f"Какой способ связи с банком вы предпочитаете?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_help_keyboard())
            InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 3001}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ENTITY_3000

        elif data == CALLBACK_BUTTON_ENTITY_6000:
            bot.send_message(chat_id=chat_id, text=f"Какой способ связи с банком вы предпочитаете?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_help_keyboard())
            InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 6001}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ENTITY_6000

        elif data == CALLBACK_BUTTON_ENTITY_10000:
            bot.send_message(chat_id=chat_id, text=f"Какой способ связи с банком вы предпочитаете?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_help_keyboard())
            InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 10001}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ENTITY_10000

        elif data == CALLBACK_BUTTON_ENTITY_ANY_COST:
            bot.send_message(chat_id=chat_id, text=f"Какой способ связи с банком вы предпочитаете?",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_help_keyboard())
            InlineCallback.update_data({"is_help_phone": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_email": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_vk": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_human": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"is_help_chat_bot": False}, f"personal/personal_{chat_id}.json")
            InlineCallback.update_data({"max price": 999999999}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ENTITY_ANY_COST

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
            bot.send_message(chat_id=chat_id, text=f"Выберите приемлемую стоимость услуг ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_entity_price_keyboard())
            InlineCallback.update_data({"get_all_types_acc": True}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ALL_TYPES_ACC_YES

        elif data == CALLBACK_BUTTON_ALL_TYPES_ACC_NO:
            bot.send_message(chat_id=chat_id, text=f"Выберите приемлемую стоимость услуг ДБО:",
                             parse_mode=telegram.ParseMode.HTML,
                             reply_markup=InlineKeyboardFactory.get_entity_price_keyboard())
            InlineCallback.update_data({"get_all_types_acc": False}, f"personal/personal_{chat_id}.json")
            return CALLBACK_BUTTON_ALL_TYPES_ACC_NO
