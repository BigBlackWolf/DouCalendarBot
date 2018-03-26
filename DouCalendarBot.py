import telebot
import config
import urllib.request
import re
import os
from bs4 import BeautifulSoup
from flask import Flask, request


server = Flask(__name__)
bot = telebot.TeleBot(config.token)
BASE_URL = 'https://dou.ua/calendar/city/%D0%9A%D0%B8%D0%B5%D0%B2/'


def soupit(url):
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    return(soup)


def cleanup(string):
    new_string = re.sub(r'\t', '', string)
    new_string = re.sub(r'\n', '', new_string)
    new_string = re.sub(r'\xa0', ' ', new_string)
    return (new_string)


def paggination(soup):
    pages = soup.find('div', class_="b-paging")
    a = pages.find_all('span')
    return(len(a)-2)


def parse(soup):
    projects = []
    block = soup.find('div', class_="col50 m-cola")
    for cluster in block.find_all('article', class_="b-postcard"):
        title = cluster.h2.text
        when_and_where = cluster.find('div', class_="when-and-where")
        date_and_price = when_and_where.find_all('span')
        date = date_and_price[0].text
        date = re.findall(r'\d+', date)
        try:
            price = date_and_price[1].text
        except:
            price = "Нет данных"
        projects.append({
            'title': cleanup(title),
            'price': cleanup(price),
            'date': date
        })
    return (projects)


def tg_message(date):
    message = ""
    soup = soupit(BASE_URL)
    pages = paggination(soup)
    for i in range(1, pages + 1):
        soup = soupit(BASE_URL + str(i))
        result = parse(soup)
        for j in result:
            for k in j['date']:
                if k == date:
                    message = message + "⭐ " + "<b>" + j['title'] + "</b>" + \
                    " (" + j['price'] + ")" + "\n"
    return (message)


@bot.message_handler(commands=['start'])
def handle_text(message):
    bot.send_message(message.chat.id, "Just send a date")


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.chat.id, 
        "I can take the date and give you some sweets")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    p = re.match(r'\d+', message.text)
    try:
        bot.send_message(chat_id=message.chat.id, text='Searching events...')
        bot.send_message(parse_mode='HTML', \
            chat_id=message.chat.id, text=tg_message(p.group(0)))
    except:
        bot.send_message(message.chat.id, "Введите корректную дату")


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
