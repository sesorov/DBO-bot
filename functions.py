import requests
import telegram
import pandas as pd
import bs4
import matplotlib
import matplotlib.pyplot as plot
import json
from telegram import Bot, Update
from setup import TOKEN
from database import BankDatabase
from functools import reduce

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


def generate_report():
    pass


def graph_price(chat_id: int = 0, is_individual: bool = True):
    if is_individual:
        banks = [dict(item, score=0) for item in db_banks.get_individuals()]
    else:
        banks = [dict(item, score=0) for item in db_banks.get_entity()]
    for bank in banks:
        if bank.get('min price') is None:
            bank['min price'] = 0
        if bank.get('max price') is None:
            bank['max price'] = 0
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #    print(dataframe)
    # df.plot(x='name', y='min price', kind='bar')
    ax = plot.gca()
    if is_individual:
        ax.set_title("Ценовой диапазон - ФИЗИЧЕСКИЕ ЛИЦА")
    else:
        ax.set_title("Ценовой диапазон - ЮРИДИЧЕСКИЕ ЛИЦА")
    # plot.gcf().subplots_adjust(bottom=0.15)
    # plot.tight_layout()
    banks = sorted(banks, key=lambda k: k['max price'], reverse=False)
    df = pd.DataFrame(banks)
    for i, bank in zip(range(0, len(banks)), banks):
        if is_individual:
            ax.text(bank['max price'] + 100, i - .25, str(bank['min price']), color='blue')
            ax.text(bank['max price'] + 1000, i - .25, str(bank['max price']), color='red')
        else:
            ax.text(bank['max price'] + 2000, i - .25, str(bank['min price']), color='blue')
            ax.text(bank['max price'] + 8000, i - .25, str(bank['max price']), color='red')
    plot.xlim(plot.ylim()[0], (12000 if is_individual else 60000))
    df.plot(kind='barh', x='name', y='max price', color='red', ax=ax)
    banks = sorted(banks, key=lambda k: k['min price'], reverse=False)
    df = pd.DataFrame(banks)
    df.plot(kind='barh', x='name', y='min price', ax=ax)
    plot.ylabel('Названия банков')
    plot.xlabel("Руб/мес")
    plot.savefig(f'graph/price_{chat_id}_{"individual" if is_individual else "entity"}.png', bbox_inches="tight")


def graph_rating(chat_id: int = 0, is_individual: bool = True):
    if is_individual:
        banks = [dict(item, score=0) for item in db_banks.get_individuals()]
    else:
        banks = [dict(item, score=0) for item in db_banks.get_entity()]
    ax = plot.gca()
    if is_individual:
        ax.set_title("Рейтинг - ФИЗИЧЕСКИЕ ЛИЦА")
    else:
        ax.set_title("Рейтинг - ЮРИДИЧЕСКИЕ ЛИЦА")
    banks = sorted(banks, key=lambda k: k['rating'], reverse=False)
    df = pd.DataFrame(banks)
    df.plot(kind='bar', x='name', y='rating', color='blue', ax=ax)
    plot.ylabel('Названия банков')
    plot.xlabel("Руб/мес")
    plot.savefig(f'graph/rating_{chat_id}_{"individual" if is_individual else "entity"}.png', bbox_inches="tight")


def calculate(chat_id):
    with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
        personal = json.load(handle)  # dictionary
        if personal['is_individual']:
            banks = [dict(item, score=0) for item in db_banks.get_individuals()]
            if not personal['is_simple']:  # standard
                for bank in banks:
                    for i in range(0, 4):
                        if personal['deposits_investments_both_account'] == i:
                            if bank['deposit investment operations'] >= i or personal[
                                'deposits_investments_both_account'] == 3:
                                bank['score'] += 1
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
                    if personal['is_expenses_control']:
                        if bank['is individual expenses control']:
                            bank['score'] += 1
                    if personal['is_gpay']:
                        if personal['is_visa']:
                            if bank['gpay visa'] == 0:
                                bank['score'] -= 1
                            elif bank['gpay visa'] == 1:
                                bank['score'] += 2
                            elif bank['gpay visa'] == 2:
                                bank['score'] += 1
                        if personal['is_mastercard']:
                            if bank['gpay mastercard'] == 0:
                                bank['score'] -= 1
                            elif bank['gpay mastercard'] == 1:
                                bank['score'] += 2
                            elif bank['gpay mastercard'] == 2:
                                bank['score'] += 1
                banks = [bank for bank in banks if
                         (bank['max price'] if bank.get('max price') is not None else 0) < personal['max price']]
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
            else:  # individual simple
                for bank in banks:
                    for i in range(0, 4):
                        if personal['deposits_investments_both_account'] == i:
                            if bank['deposit investment operations'] >= i or personal[
                                'deposits_investments_both_account'] == 3:
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

        else:  # entity
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
                banks = [bank for bank in banks if
                         (bank['max price'] if bank.get('max price') is not None else 0) < personal['max price']]
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

            else:  # entity standard
                avg_rating = sum(bank['rating'] for bank in banks) / len(banks)
                avg_markswebb = sum(bank['rating markswebb'] for bank in banks) / len(banks)

                for bank in banks:
                    for i in range(0, 4):
                        if personal['notify'] == i:
                            if bank['is SMS email push'] == i:
                                bank['score'] += 2
                            elif bank['is SMS email push'] > i:
                                bank['score'] += 1

                    if personal['send_mail']:
                        if bank['is mail to bank']:
                            bank['score'] += 2
                    elif bank['is mail to bank']:
                        bank['score'] += 1

                    if personal['salary_registers']:
                        if bank['is send registers for salary']:
                            bank['score'] += 2
                    elif bank['is send registers for salary']:
                        bank['score'] += 1

                    if personal['form_currency_transactions']:
                        if bank['is formation currency transactions']:
                            bank['score'] += 2
                    elif bank['is formation currency transactions']:
                        bank['score'] += 1

                    if personal['is_multicurrency']:
                        if bank['multicurrency payments']:
                            bank['score'] += 2
                    elif bank['multicurrency payments']:
                        bank['score'] += 1

                    if personal['notify_partner']:
                        if bank['partners notification about payments']:
                            bank['score'] += 2
                    elif bank['partners notification about payments']:
                        bank['score'] += 1

                    if personal['get_all_types_acc']:
                        if bank['all types of accounts and statements']:
                            bank['score'] += 2
                    elif bank['all types of accounts and statements']:
                        bank['score'] += 1

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

                    if bank.get('max price') is not None:
                        if personal['max price'] > bank['max price']:
                            bank['score'] += 1

                    if bank['rating'] < avg_rating:
                        bank['score'] -= 1

                    if bank['rating markswebb'] < avg_markswebb:
                        bank['score'] -= 1

                banks = [bank for bank in banks if
                         (bank['min price'] if bank.get('min price') is not None else 0) < personal[
                             'max price']]  # sorting by price
                banks = sorted(banks, key=lambda k: k['score'], reverse=True)  # sorting by score
                top = [bank for bank in banks if bank['score'] == banks[0]['score']]  # only leaders
                top = sorted(top, key=lambda k: k['rating'], reverse=True)  # sorting by user's rating
                top = sorted(top, key=lambda k: k['rating markswebb'],
                             reverse=True)  # sorting by overall markswebb's rating

                message = "Исходя из ваших предпочтений и рейтинга, самые подходящие банки:\n"
                if len(top) > 3:
                    top_3 = top[:3]
                index = 1
                for bank in (top_3 if len(top) > 3 else top):
                    message += f"{index}. {bank['name']}\n"
                    index += 1
                message += "Общий полученный рейтинг лучших банков:\n"
                index = 1
                for bank in top:
                    message += f"{index}. {bank['name']} - {bank['score']} очков\n"
                    index += 1
                message += "Общий рейтинг банков:\n"
                index = 1
                for bank in banks:
                    message += f"{index}. {bank['name']} - {bank['score']} очков\n"
                    index += 1
                bot.send_message(chat_id=chat_id, text=message)
