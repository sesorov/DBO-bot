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
            banks = db_banks.get_individuals()
        else:
            banks = [dict(item, score=0) for item in db_banks.get_entity()]  # adding a score value to sort
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
            message = f"Исходя из ваших предпочтений и рейтинга, самые подходящие банки:\n1.{top[0]['name']}\n2.{top[1]['name']}\n3.{top[3]['name']}"
            bot.send_message(chat_id=chat_id, text=message)
