import re
import sqlite3
import os
import requests

import telebot
from bs4 import BeautifulSoup
from flask import Flask, request
from apscheduler.schedulers.blocking import BlockingScheduler

import config

server = Flask(__name__)
bot = telebot.TeleBot(config.token)
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
BASE_URL = 'https://dou.ua/calendar/city/%D0%9A%D0%B8%D0%B5%D0%B2/'


def soupit(url):
    page = requests.get(url, headers=headers).content
    soup = BeautifulSoup(page, "html.parser")
    return soup


def cleanup(string):
    new_string = re.sub(r'[\t\n]', '', string)
    return new_string


# Getting number of pages
def paggination(soup):
    pages = soup.find('div', class_="b-paging")
    a = pages.find_all('span')
    return len(a) - 2


# Function to parse and update information in base
def parse():
    soup = soupit(BASE_URL)
    pages = paggination(soup)
    result = []
    for i in range(1, pages + 1):
        soup = soupit(BASE_URL + str(i))
        block = soup.find('div', class_="col50 m-cola")
        block2 = list(block)[2:49]
        for j in block2:
            # Finding exactly tags, which contains useful information or skip i in block
            if not hasattr(j, 'text'):
                continue
            if j.find('a').parent.name == "div" and j.find('a').text != "RSS":
                # Formatting parsed date
                date = (j.find('a')).get('href')
                date = re.search(r'\d+\-\d+\-\d+', date)
                date = date.group(0)
                date = re.sub(r'-', '.', date)
                a = date[5:7]
                b = date[8:]
                date = b + "." + a
            elif j.find('a').parent.name == "h2":
                title = j.find('a').parent.text
                href = j.find('a')['href']
                when_and_where = j.find('div', class_="when-and-where")
                date_and_price = when_and_where.find_all('span')
                try:
                    price = date_and_price[1].text
                except IndexError:
                    price = 'Нет данных'
                result.append((cleanup(title), cleanup(price), date, href))
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()
    cursor.executemany("INSERT OR REPLACE INTO calendar (title, price, date, href) VALUES (?, ?, ?, ?);", result)
    connection.commit()
    connection.close()


# Composing message to be sent
def tg_message(date):
    message = ""
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()
    title = cursor.execute("SELECT title, price, href FROM calendar WHERE date=?", (date,))
    for i in title.fetchall():
        message = message + "⭐ " + "<b>" + i[0] + "</b>" + \
                  " (" + i[1] + ")" + "\n" + i[2] + "\n"
    connection.close()
    return message


# Defining actions for bot
@bot.message_handler(commands=['start'])
def handle_text(message):
    bot.send_message(message.chat.id, "⌚ Введите дату в формате 'дд.ММ', чтобы увидеть запланированые мероприятия")


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.chat.id,
                     "Введите дату в формате 'дд.ММ' и я покажу события на этот день ☕")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    p = re.match(r'(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[012])', message.text)
    if p is not None:
        try:
            bot.send_message(parse_mode='HTML', chat_id=message.chat.id, text=tg_message(p.group(0)))
        except:
            bot.send_message(message.chat.id, "ℹ Нет событий на этот день ℹ")
    else:
        bot.send_message(message.chat.id, "ℹ Введите дату в формате 'дд.ММ' ℹ")


# Setting web-hooks
@server.route('/' + config.token, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "POST", 200


@server.route("/")
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url=config.url + config.token)
    return "CONNECTED", 200


server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

# Every day updates to Database
schedule = BlockingScheduler()
schedule.add_job(parse, 'cron', day_of_week='mon-sun', hour=24)
schedule.start()