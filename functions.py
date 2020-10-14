import requests
import telegram
import pandas as pd
import bs4
import matplotlib
import matplotlib.pyplot as plot
import json
import PIL
from telegram import Bot, Update
from setup import TOKEN
from database import BankDatabase
from functools import reduce
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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


def generate_report(chat_id: int = 0, is_individual: bool = True):
    graph_rating(is_individual)
    graph_rating_markswebb(is_individual)
    graph_price(is_individual)
    c = canvas.Canvas(f"analytics_{chat_id}.pdf", pagesize=A4)
    pdfmetrics.registerFont(TTFont('FreeSans', 'fonts/FreeSans.ttf'))
    c.setFont(psfontname='FreeSans', size=18)
    c.drawCentredString(300, 820, "Полный отчёт по ДБО")
    c.setFont(psfontname='FreeSans', size=16)
    c.drawCentredString(300, 780, "Ценообразование")

    #  pricing info after this comment
    text = c.beginText(25, 550)
    text.setFont(psfontname='FreeSans', size=10)
    c.drawImage(f"graph/price_{'individual' if is_individual else 'entity'}.png", 125, 575, 350, 200)
    for line in generate_price_lines(is_individual=is_individual)[:40]:  # we have only 40 lines of page left
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    text = c.beginText(25, 750)
    text.setFont(psfontname='FreeSans', size=10)
    for line in generate_price_lines(is_individual=is_individual)[40:]:
        text.textLine(line)
    c.drawText(text)
    c.showPage()

    #  card and credit info for individuals
    if is_individual:
        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Карты и кредиты")

        # cards and credits
        text = c.beginText(25, 750)
        text.setFont(psfontname='FreeSans', size=10)
        for line in generate_cards_credits_individual()[:60]:
            text.textLine(line)
        c.drawText(text)
        c.showPage()
        text = c.beginText(25, 750)
        text.setFont(psfontname='FreeSans', size=10)
        for line in generate_cards_credits_individual()[60:]:
            text.textLine(line)
        c.drawText(text)
        c.showPage()

        # gpay
        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Поддержка Google Pay")
        tab = generate_gpay_table()
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=80, y=300)
        c.showPage()
    else:
        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "SMS-, e-mail-, push-уведомления")
        tab = generate_notification_table()
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans'),
            ('FONTNAME', (3, 0), (3, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=150, y=400)
        c.showPage()

        # send mail
        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Отправка писем, заверенных электронной подписью")
        tab = generate_minor_tables(5)
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=125, y=400)
        c.showPage()

        # реестры зп

        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Отправка реестров на з/плату")
        tab = generate_minor_tables(6)
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=125, y=400)
        c.showPage()

        # Формирование сведений о валютных операциях

        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Формирование сведений о валютных операциях")
        tab = generate_minor_tables(8)
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=125, y=400)
        c.showPage()

        # Мультивалютные платежи

        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Мультивалютные платежи")
        tab = generate_minor_tables(9)
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=125, y=400)
        c.showPage()

        # Уведомление партнеров о платежах

        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Уведомление партнеров о платежах")
        tab = generate_minor_tables(10)
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=125, y=400)
        c.showPage()

        # Все виды счетов и выписок

        c.setFont(psfontname='FreeSans', size=16)
        c.drawCentredString(300, 820, "Все виды счетов и выписок")
        tab = generate_minor_tables(11)
        t = Table(tab)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'FreeSans'),
            ('FONTNAME', (1, 0), (1, -1), 'FreeSans'),
            ('FONTNAME', (2, 0), (2, -1), 'FreeSans')
        ]))
        t.wrapOn(canv=c, aW=200, aH=500)
        t.drawOn(canvas=c, x=125, y=400)
        c.showPage()

    c.save()


def generate_minor_tables(id):
    banks = [dict(item, score=0) for item in db_banks.get_entity()]
    banks_tables = []
    data = [["Название", "Поддерживает", "Не поддерживает"]]
    for bank in banks:
        sup = '+'
        not_sup = '+'
        if bank[list(bank.keys())[id]] == 0:
            sup = ''
        elif bank[list(bank.keys())[id]] == 1:
            not_sup = ''
        data.append([bank['name'], sup, not_sup])
    banks_tables.append(data)
    return data


def generate_notification_table():
    banks = [dict(item, score=0) for item in db_banks.get_entity()]
    data = [["Название", "SMS", "e-mail", "PUSH"]]
    for bank in banks:
        sms_sup = '-'
        email_sup = '-'
        push_sup = '-'
        if bank['is SMS email push'] == 1:
            sms_sup = 'ДА'
        elif bank['is SMS email push'] == 2:
            sms_sup = 'ДА'
            email_sup = 'ДА'
        elif bank['is SMS email push'] == 3:
            sms_sup = 'ДА'
            email_sup = 'ДА'
            push_sup = 'ДА'
        data.append([bank['name'], sms_sup, email_sup, push_sup])
    return data


def generate_gpay_table():
    banks = [dict(item, score=0) for item in db_banks.get_individuals()]
    data = [["Название", "GPay VISA", "GPay Mastercard"]]
    for bank in banks:
        visa_sup = '-'
        mastercard_sup = '-'
        if bank['gpay visa'] == 1:
            visa_sup = 'ДА'
        elif bank['gpay visa'] == 2:
            visa_sup = 'С ОГРАНИЧЕНИЯМИ'
        if bank['gpay mastercard'] == 1:
            mastercard_sup = 'ДА'
        elif bank['gpay mastercard'] == 2:
            mastercard_sup = 'С ОГРАНИЧЕНИЯМИ'
        data.append([bank['name'], visa_sup, mastercard_sup])
    return data


def generate_cards_credits_individual():
    banks = [dict(item, score=0) for item in db_banks.get_individuals()]
    text = ["Подробная информация по картам и кредитам для физических лиц:"]
    index = 1
    for bank in banks:
        text.append(
            f"{index}. {bank['name']} (лицензия №{bank['license']}): возможность заказать карту {'при' if bank['is possible order'] else 'от'}сутствует.")
        text.append(f"Дополнительная информация по картам: {bank['card additional']}")
        text.append(f"Дополнительная информация по кредитам:")
        text.append(f" - {bank['credit info additional']}")
        text.append(
            "------------------------------------------------------------------------------------------------------------")
        index += 1
    return text


def generate_price_lines(is_individual: bool = True) -> list:
    if is_individual:
        banks = [dict(item, score=0) for item in db_banks.get_individuals()]
        text = ["Подробная информация по ценообразованию для физических лиц:"]
        index = 1
        for bank in banks:
            text.append(
                f"{index}. {bank['name']} (лицензия №{bank['license']}) - от {bank['min price']} до {bank['max price']} руб/мес без учёта СМС-банкинга.")
            text.append(f"Стоимость СМС-банкинга: {bank['SMS additional']} руб/мес")
            text.append(f"Страница с доступными тарифами: {bank['price additional']}")
            text.append(
                "------------------------------------------------------------------------------------------------------------")
            index += 1
        return text
    else:
        banks = [dict(item, score=0) for item in db_banks.get_entity()]
        text = ["Подробная информация по ценообразованию для юридических лиц:"]
        index = 1
        for bank in banks:
            text.append(
                f"{index}. {bank['name']} (лицензия №{bank['license']}) - от {bank['min price'] if bank.get('min price') is not None else 0} до {bank['max price'] if bank.get('max price') != 0 else 'НЕТ ДАННЫХ'} руб/мес.")
            text.append(f"Страница с доступными тарифами: {bank['price addition']}")
            text.append(
                "------------------------------------------------------------------------------------------------------------")
            index += 1
        return text


def graph_price(is_individual: bool = True):
    if is_individual:
        banks = [dict(item, score=0) for item in db_banks.get_individuals()]
    else:
        banks = [dict(item, score=0) for item in db_banks.get_entity()]
    for bank in banks:
        if bank.get('min price') is None:
            bank['min price'] = 0
        if is_individual:
            bank['min price'] += bank['SMS additional']
        if bank.get('max price') is None:
            bank['max price'] = 0
    ax = plot.gca()
    fig = ax.get_figure()
    if is_individual:
        ax.set_title("Ценовой диапазон - ФИЗИЧЕСКИЕ ЛИЦА (с учетом СМС-банкинга)")
    else:
        ax.set_title("Ценовой диапазон - ЮРИДИЧЕСКИЕ ЛИЦА")
    banks = sorted(banks, key=lambda k: k['max price'], reverse=False)
    df = pd.DataFrame(banks)
    for i, bank in zip(range(0, len(banks)), banks):
        if is_individual:
            ax.text(bank['max price'] + 100, i - .25, str(bank['min price']), color='blue')
            ax.text(bank['max price'] + 20000, i - .25, str(bank['max price']), color='red')
        else:
            ax.text(bank['max price'] + 2000, i - .25, str(bank['min price']), color='blue')
            ax.text(bank['max price'] + 8000, i - .25, str(bank['max price']), color='red')
    plot.xlim(plot.ylim()[0], (370000 if is_individual else 60000))
    df.plot(kind='barh', x='name', y='max price', color='red', ax=ax)
    banks = sorted(banks, key=lambda k: k['min price'], reverse=False)
    df = pd.DataFrame(banks)
    df.plot(kind='barh', x='name', y='min price', ax=ax)
    plot.ylabel('Названия банков')
    plot.xlabel("Руб/мес")
    plot.savefig(f'graph/price_{"individual" if is_individual else "entity"}.png', bbox_inches="tight")
    plot.close(fig)


def graph_rating(is_individual: bool = True):
    if is_individual:
        banks = [dict(item, score=0) for item in db_banks.get_individuals()]
    else:
        banks = [dict(item, score=0) for item in db_banks.get_entity()]
    ax = plot.gca()
    fig = ax.get_figure()
    if is_individual:
        ax.set_title("Рейтинг - ФИЗИЧЕСКИЕ ЛИЦА")
    else:
        ax.set_title("Рейтинг - ЮРИДИЧЕСКИЕ ЛИЦА")
    banks = sorted(banks, key=lambda k: k['rating'], reverse=False)
    df = pd.DataFrame(banks)
    df.plot(kind='bar', x='name', y='rating', color='blue', ax=ax)
    plot.ylabel('Оценка')
    plot.xlabel("Названия банков")
    plot.savefig(f'graph/rating_{"individual" if is_individual else "entity"}.png', bbox_inches="tight")
    plot.close(fig)


def graph_rating_markswebb(is_individual: bool = True):
    if is_individual:
        banks = [dict(item, score=0) for item in db_banks.get_individuals()]
    else:
        banks = [dict(item, score=0) for item in db_banks.get_entity()]
    ax = plot.gca()
    fig = ax.get_figure()
    if is_individual:
        ax.set_title("Рейтинг Markswebb - ФИЗИЧЕСКИЕ ЛИЦА")
    else:
        ax.set_title("Рейтинг Markswebb - ЮРИДИЧЕСКИЕ ЛИЦА")
    banks = sorted(banks, key=lambda k: k['rating markswebb'], reverse=False)
    df = pd.DataFrame(banks)
    df.plot(kind='bar', x='name', y='rating markswebb', color='blue', ax=ax)
    plot.ylabel('Оценка')
    plot.xlabel("Названия банков")
    plot.savefig(f'graph/rating_markswebb_{"individual" if is_individual else "entity"}.png', bbox_inches="tight")
    plot.close(fig)


def calculate(chat_id):
    with open(f"personal/personal_{chat_id}.json", mode='r') as handle:
        personal = json.load(handle)  # dictionary
        if personal['is_individual']:
            banks = [dict(item, score=0) for item in db_banks.get_individuals()]
            if not personal['is_simple']:  # standard
                avg_rating = sum(bank['rating'] for bank in banks) / len(banks)
                avg_markswebb = sum(bank['rating markswebb'] for bank in banks) / len(banks)
                for bank in banks:
                    for i in range(0, 4):
                        if personal['deposits_investments_both_account'] == i:
                            if bank['deposit investment operations'] >= i or personal[
                                'deposits_investments_both_account'] == 3:
                                bank['score'] += 1
                                break
                    if personal['is_help_phone']:
                        if 1 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_email']:
                        if 2 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_vk']:
                        if 3 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_human']:
                        if 4 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_bot']:
                        if 5 in bank['help']:
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
                        if personal['sms']:
                            bank['min price'] += bank['SMS additional']
                        if bank['rating'] < avg_rating:
                            bank['score'] -= 1
                        if bank['rating markswebb'] < avg_markswebb:
                            bank['score'] -= 1
                banks = [bank for bank in banks if
                         (bank['min price'] if bank.get('min price') is not None else 0) <= personal['max price']]
                banks = [bank for bank in banks if
                         (bank['max price'] if bank.get('max price') is not None else 0) >= personal['min price']]
                banks = sorted(banks, key=lambda k: k['score'], reverse=True)
                top = [bank for bank in banks if bank['score'] == banks[0]['score']]
                top = sorted(top, key=lambda k: k['rating'], reverse=True)
                top = sorted(top, key=lambda k: k['rating markswebb'], reverse=True)

                for bank in banks:
                    print(f"{bank['name']} - {bank['score']}")

                message = "Исходя из ваших предпочтений и рейтинга, самые подходящие банки:\n"
                if len(top) > 3:
                    top = top[:3]
                index = 1
                for bank in top:
                    message += f"{index}. {bank['name']}\n"
                    index += 1
                bot.send_message(chat_id=chat_id, text=message)
            else:  # individual simple
                avg_rating = sum(bank['rating'] for bank in banks) / len(banks)
                avg_markswebb = sum(bank['rating markswebb'] for bank in banks) / len(banks)
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
                    if personal['is_help_phone']:
                        if 1 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_email']:
                        if 2 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_vk']:
                        if 3 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_human']:
                        if 4 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_bot']:
                        if 5 in bank['help']:
                            bank['score'] += 1
                    if bank['rating'] < avg_rating:
                        bank['score'] -= 1
                    if bank['rating markswebb'] < avg_markswebb:
                        bank['score'] -= 1
                banks = sorted(banks, key=lambda k: k['score'], reverse=True)
                top = [bank for bank in banks if bank['score'] == banks[0]['score']]
                if personal['most_important'] == 'price':
                    top = sorted(top, key=lambda k: k['min price'] if k.get('min price') else 0, reverse=False)
                elif personal['most_important'] == 'reliability':
                    top = sorted(top, key=lambda k: k['rating'], reverse=True)
                elif personal['most_important'] == 'convenience':
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
                avg_rating = sum(bank['rating'] for bank in banks) / len(banks)
                avg_markswebb = sum(bank['rating markswebb'] for bank in banks) / len(banks)
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
                    if personal['is_help_phone']:
                        if 1 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_email']:
                        if 2 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_vk']:
                        if 3 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_human']:
                        if 4 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_bot']:
                        if 5 in bank['help']:
                            bank['score'] += 1

                    if bank['rating'] < avg_rating:
                        bank['score'] -= 1

                    if bank['rating markswebb'] < avg_markswebb:
                        bank['score'] -= 1

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

                    if personal['is_help_phone']:
                        if 1 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_email']:
                        if 2 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_vk']:
                        if 3 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_human']:
                        if 4 in bank['help']:
                            bank['score'] += 1
                    if personal['is_help_chat_bot']:
                        if 5 in bank['help']:
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
