import re
import sqlite3
import os
import urllib.request
<<<<<<< HEAD

import telebot
from bs4 import BeautifulSoup
from flask import Flask, request
from apscheduler.schedulers.blocking import BlockingScheduler

import config
=======
import re
import os
from bs4 import BeautifulSoup
from flask import Flask, request

>>>>>>> 0d8635d17f26d932dfd33331c2e0048838405f85

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

<<<<<<< HEAD
#Getting number of pages
=======

>>>>>>> 0d8635d17f26d932dfd33331c2e0048838405f85
def paggination(soup):
    pages = soup.find('div', class_="b-paging")
    a = pages.find_all('span')
    return(len(a)-2)

<<<<<<< HEAD
#Function to parse and update information in base
def parse():
=======

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
>>>>>>> 0d8635d17f26d932dfd33331c2e0048838405f85
    soup = soupit(BASE_URL)
    pages = paggination(soup)
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()
    try:
        cursor.execute(config.delete_table)
        cursor.execute(config.create_table)
    except:
        cursor.execute(config.create_table)
    for i in range(1, pages + 1):
        soup = soupit(BASE_URL + str(i))
<<<<<<< HEAD
        block = soup.find('div', class_="col50 m-cola")
        for i in block:
            #Finding exactly tags, which contains useful information or skip i in block
            try:
                if i.find('a').parent.name=="div" and i.find('a').text!="RSS":
                    #Formatting parsed date
                    date = (i.find('a')).get('href')
                    date = re.search(r'\d+\-\d+\-\d+', date)
                    date = date.group(0)
                    date = re.sub(r'-', '.', date)
                    a = date[5:7]
                    b = date[8:]
                    date = b + "." + a
                elif i.find('a').parent.name=="h2":
                    title = i.find('a').parent.text
                    when_and_where = i.find('div', class_="when-and-where")
                    date_and_price = when_and_where.find_all('span')
                    try:
                        price = date_and_price[1].text
                    except:
                        price = "Нет данных"
                    cursor.execute("INSERT INTO calendar (title, price, date) VALUES (? ,? ,?);",(cleanup(title),cleanup(price), date))
            except:
                pass
    connection.commit()
    connection.close()
    return()

#Composing message to be sent
def tg_message(date):
    message = ""
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()
    title = cursor.execute("SELECT title, price FROM calendar WHERE date=?", (date,))
    for i in title.fetchall():
        message = message + "⭐ " + "<b>" + i[0] + "</b>" + \
                  " (" + i[1] + ")" + "\n"
    connection.close()
    return (message)

#Defining actions for bot
@bot.message_handler(commands=['start'])
def handle_text(message):
    bot.send_message(message.chat.id, "⌚ Введите дату в формате 'дд.ММ', чтобы увидеть запланированые мероприятия")
=======
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
>>>>>>> 0d8635d17f26d932dfd33331c2e0048838405f85


@bot.message_handler(commands=['help'])
def handle_text(message):
<<<<<<< HEAD
    bot.send_message(message.chat.id,
        "Введите дату в формате 'дд.ММ' и я покажу события на этот день ☕")
=======
    bot.send_message(message.chat.id, 
        "I can take the date and give you some sweets")
>>>>>>> 0d8635d17f26d932dfd33331c2e0048838405f85


@bot.message_handler(content_types=['text'])
def handle_text(message):
<<<<<<< HEAD
    p = re.match(r'(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[012])', message.text)
    if p is not None:
        try:
            bot.send_message(parse_mode='HTML', \
                chat_id=message.chat.id, text=tg_message(p.group(0)))
        except:
            bot.send_message(message.chat.id, "ℹ Нет событий на этот день ℹ")
    else:
        bot.send_message(message.chat.id, "ℹ Введите дату в формате 'дд.ММ' ℹ")

#Setting web-hooks
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


#Every day updates to Database
schedule = BlockingScheduler()
schedule.add_job(parse, 'cron', day_of_week='mon-sun', hour=24)
schedule.start()
=======
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
>>>>>>> 0d8635d17f26d932dfd33331c2e0048838405f85
