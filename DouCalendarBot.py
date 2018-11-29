import re
import sqlite3
import os
import datetime

import telebot
from telebot import types
from flask import Flask, request

import config

server = Flask(__name__)
bot = telebot.TeleBot(config.token)

# Creating keyboard for usual setuation
markup_menu = types.ReplyKeyboardMarkup()
btn_test = types.KeyboardButton("Сегодня")
btn_test1 = types.KeyboardButton("Завтра")
btn_test2 = types.KeyboardButton('Послезавтра')
btn_test3 = types.KeyboardButton('На этой неделе')
btn_test4 = types.KeyboardButton('На следующей неделе')
# btn_click = types.KeyboardButton('Настройки')
markup_menu.row(btn_test, btn_test1, btn_test2)
markup_menu.row(btn_test3, btn_test4)
# markup_menu.row(btn_click)

# Creating keyboard for settings
markup_menu_settings = types.ReplyKeyboardMarkup()
btn_change = types.KeyboardButton("Изменить")
markup_menu_settings.row(btn_change)


# Composing message to be sent
def tg_message(date=None, week=None):
    message = ""
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()
    if date:
        title = cursor.execute("SELECT title, price, href FROM calendar WHERE date=?", (date,))
    else:
        title = cursor.execute("SELECT title, price, href FROM calendar WHERE week=?", (week,))
    for i in title.fetchall():
        message = message + "⭐ " + "<b>" + i[0] + "</b>" + " (" + i[1] + ")" + "\n" + i[2] + "\n\n"
    connection.close()
    return message


# Defining actions for bot
@bot.message_handler(commands=['start'])
def handle_text(message):
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT enabled_alarm FROM users WHERE chat_id=?", (message.chat.id,)).fetchone()[0]
    except:
        cursor.execute("INSERT INTO users (chat_id, enabled_alarm) VALUES (? ,?)", (message.chat.id, 0))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, "⌚ Введите дату в формате 'дд.ММ', чтобы увидеть запланированые мероприятия",
                     reply_markup=markup_menu)


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.chat.id,
                     "Введите дату в формате 'дд.ММ' и я покажу события на этот день ☕")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    p = message.text
    if message.text == "Сегодня":
        date = datetime.date.today()
        p = str(datetime.datetime.strftime(date, "%d.%m"))
    elif message.text == "Завтра":
        now = datetime.date.today()
        date = now + datetime.timedelta(days=1)
        p = str(datetime.datetime.strftime(date, "%d.%m"))
    elif message.text == "Послезавтра":
        now = datetime.date.today()
        date = now + datetime.timedelta(days=2)
        p = str(datetime.datetime.strftime(date, "%d.%m"))
    elif message.text == "На этой неделе":
        p = datetime.date.today().isocalendar()[1]
    elif message.text == "На следующей неделе":
        p = datetime.date.today().isocalendar()[1] + 1 % 52
    elif message.text == "Настройки":
        connection = sqlite3.connect('events.db')
        cursor = connection.cursor()
        alarm = cursor.execute("SELECT enabled_alarm FROM users WHERE chat_id=?", (message.chat.id,)).fetchone()[0]
        if alarm == 0:
            massage = "Напоминания отключены"
        else:
            massage = "Напоминания включены"
        bot.send_message(message.chat.id, massage, reply_markup=markup_menu_settings)
        connection.close()
        return 
    elif message.text == "Изменить":
        connection = sqlite3.connect('events.db')
        cursor = connection.cursor()
        alarm = cursor.execute("SELECT enabled_alarm FROM users WHERE chat_id=?", (message.chat.id,)).fetchone()[0]
        if alarm == 0:
            cursor.execute("UPDATE users SET enabled_alarm=? WHERE chat_id=?", (1, message.chat.id))
            bot.send_message(message.chat.id, "Напоминания установлены", reply_markup=markup_menu)
        else:
            cursor.execute("UPDATE users SET enabled_alarm=? WHERE chat_id=?", (0, message.chat.id))
            bot.send_message(message.chat.id, "Напоминания деактивированы", reply_markup=markup_menu)
        connection.commit()
        connection.close()
        return 
    try:
        if isinstance(p, int):
            bot.send_message(parse_mode='HTML',
                             chat_id=message.chat.id, text=tg_message(week=p))
        elif str(p) == p:
            bot.send_message(parse_mode='HTML',
                             chat_id=message.chat.id, text=tg_message(p))
    except:
        bot.send_message(message.chat.id, "ℹ Нет событий на этот день ℹ")


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
