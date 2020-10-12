import requests
import telegram
import json
from telegram import Bot, Update
from setup import TOKEN
from database import BankDatabase

bot = Bot(
    token=TOKEN,
    # base_url=PROXY,  # delete it if connection via VPN
)

db_banks = BankDatabase()


def extract_price(source, is_min):
    try:
        return int(source['min price'] if is_min else source['max price'])
    except KeyError:
        return 0


def calculate(chat_id):
    with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
        personal = json.load(handle)  # dictionary
        if personal['is_individual']:
            banks = [dict(item, score=0) for item in db_banks.get_individuals()]
            if not personal['is_simple']:
                pass
            else:
                for bank in banks:
                    for i in range(0, 4):
                        if personal['deposits_investments_both_account'] == i:
                            if bank['deposit investment operations'] >= i or personal['deposits_investments_both_account'] == 3:
                                bank['score'] += 1
                    if personal['is_expenses_control']:
                        if bank['is individual expenses control']:
                            bank['score'] += 1
                    if personal['is_gpay']:
                        if bank['gpay visa'] == 0:
                            bank['score'] -= 1
                        elif bank['gpay visa'] == 1:
                            bank['score'] += 2
                        elif bank['gpay visa'] == 2:
                            bank['score'] += 1
                        if bank['gpay mastercard'] == 0:
                            bank['score'] -= 1
                        elif bank['gpay mastercard'] == 1:
                            bank['score'] += 2
                        elif bank['gpay mastercard'] == 2:
                            bank['score'] += 1

                        bank['score'] += bank['gpay visa']
                        bank['score'] += bank['gpay mastercard']
                    if personal['is_help_phone'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_email'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_vk'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_chat_human'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_chat_bot'] in bank['help']:
                        bank['score'] += 1
                banks = sorted(banks, key=lambda k: k['score'], reverse=True)
                top = [bank for bank in banks if bank['score'] == banks[0]['score']]
                if personal['most_important'] == 'price':
                    top = sorted(top, key=lambda k: k['min price'] if k.get('min price') else 0, reverse=False)
                elif personal['most_important'] == 'reliability':
                    top = sorted(top, key=lambda k: k['rating'], reverse=True)
                elif personal['most_important'] == 'convenience':
                    top = sorted(top, key=lambda k: k['rating markswebb'], reverse=True)
                top = sorted(top, key=lambda k: k['rating'], reverse=True)
                top = sorted(top, key=lambda k: k['rating markswebb'], reverse=True)
                message = "Исходя из ваших предпочтений и рейтинга, самые подходящие банки:\n"
                if len(top) > 3:
                    top = top[:3]
                index = 1
                for bank in top:
                    message += f"{index}. {bank['name']}\n"
                    index += 1
                bot.send_message(chat_id=chat_id, text=message)

        else:
            banks = [dict(item, score=0) for item in db_banks.get_entity()]  # adding a score value to sort
            if personal['is_simple']:
                for bank in banks:
                    for i in range(0, 4):
                        if personal['notify'] == i:
                            if bank['is SMS email push'] == i:
                                bank['score'] += 2
                            elif bank['is SMS email push'] > i:
                                bank['score'] += 1
                    if personal['using_currency']:
                        if bank['is formation currency transactions']:
                            bank['score'] += 2
                        if bank['multicurrency payments']:
                            bank['score'] += 3
                    if personal['is_help_phone'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_email'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_vk'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_chat_human'] in bank['help']:
                        bank['score'] += 1
                    if personal['is_help_chat_bot'] in bank['help']:
                        bank['score'] += 1

                    # minor
                    if bank['is mail to bank']:
                        bank['score'] += 1
                    if bank['is send registers for salary']:
                        bank['score'] += 1
                    if bank['partners notification about payments']:
                        bank['score'] += 1
                    if bank['all types of accounts and statements']:
                        bank['score'] += 1
                banks = [bank for bank in banks if (bank['max price'] if bank.get('max price') is not None else 0) < personal['max price']]
                banks = sorted(banks, key=lambda k: k['score'], reverse=True)
                top = [bank for bank in banks if bank['score'] == banks[0]['score']]
                top = sorted(top, key=lambda k: k['rating'], reverse=True)
                top = sorted(top, key=lambda k: k['rating markswebb'], reverse=True)

                message = "Исходя из ваших предпочтений и рейтинга, самые подходящие банки:\n"
                if len(top) > 3:
                    top = top[:3]
                index = 1
                for bank in top:
                    message += f"{index}. {bank['name']}\n"
                    index += 1
                bot.send_message(chat_id=chat_id, text=message)

            else:
                for bank in banks:
                    for i in range(0, 4):
                        if personal['notify'] == i:
                            if bank['is SMS email push'] >= i:
                                bank['score'] += 1

                    if personal['send_mail']:
                        if bank['is mail to bank']:
                            bank['score'] += 1

                    if personal['salary_registers']:
                        if bank['is send registers for salary']:
                            bank['score'] += 1

                    if personal['form_currency_transactions']:
                        if bank['is formation currency transactions']:
                            bank['score'] += 1

                    if personal['is_multicurrency']:
                        if bank['multicurrency payments']:
                            bank['score'] += 1

                    if personal['notify_partner']:
                        if bank['partners notification about payments']:
                            bank['score'] += 1

                    if personal['get_all_types_acc']:
                        if bank['all types of accounts and statements']:
                            bank['score'] += 1

                banks = sorted(banks, key=lambda k: k['score'], reverse=True)
                top = [bank for bank in banks if bank['score'] == banks[0]['score']]
                for bank in top:
                    for i in range(0, 4):
                        if personal['notify'] == i:
                            if bank['is SMS email push'] == i:
                                bank['score'] += 1
                                break
                            else:
                                bank['score'] -= 1
                                break

                    if personal['send_mail'] != bank['is mail to bank']:
                        bank['score'] -= 1

                    if personal['salary_registers'] != bank['is send registers for salary']:
                        bank['score'] -= 1

                    if personal['form_currency_transactions'] != bank['is formation currency transactions']:
                        bank['score'] -= 1

                    if personal['is_multicurrency'] != bank['multicurrency payments']:
                        bank['score'] -= 1

                    if personal['notify_partner'] != bank['partners notification about payments']:
                        bank['score'] -= 1

                    if personal['get_all_types_acc'] != bank['all types of accounts and statements']:
                        bank['score'] -= 1

                top = sorted(top, key=lambda k: k['rating'], reverse=True)
                top = sorted(top, key=lambda k: k['score'], reverse=True)

                message = "Исходя из ваших предпочтений и рейтинга, самые подходящие банки:\n"
                if len(top) > 3:
                    top = top[:3]
                index = 1
                for bank in top:
                    message += f"{index}. {bank['name']}\n"
                    index += 1
                bot.send_message(chat_id=chat_id, text=message)
