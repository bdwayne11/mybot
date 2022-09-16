import os
import requests
import time
import re

from datetime import datetime
from dotenv import load_dotenv
import telebot
from telebot import types


if __name__== '__main__':
    load_dotenv()

    TG_TOKEN = os.getenv('TOKEN_TG')
    PUSH_HOUSE_TOKEN = os.getenv('TOKEN_PUSH_HOUSE')

    bot = telebot.TeleBot(TG_TOKEN)
    URL = f'http://api.push.house/api/statistics/{PUSH_HOUSE_TOKEN}/data/'

    pattern = r'^\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2}$'

    RETRY_TIME = 15


    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        alltime = types.KeyboardButton('/alltime')
        my_time = types.KeyboardButton('/mytime')
        markup.add(alltime, my_time)
        mess = f'Привет, <b>{message.from_user.first_name}</b>\nВыбери, пожалуйста, за какой период ты хочешь статистику. /alltime - за все время, /mytime - за заданный тобой период.'
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)


    @bot.message_handler(commands=['alltime'])
    def alltime(message):
        URL_alltime = URL + '2010-01-01'
        try:
            response = requests.get(URL_alltime).json()
        except Exception:
            bot.send_message(message.chat.id, f'Нет доступа к эндпоинту {URL}')
        response_str = str(response)
        bot.send_message(message.chat.id, response_str)


    @bot.message_handler(commands=['mytime'])
    def mytime(message):
        try:
            msg = bot.send_message(message.chat.id,
            'Укажите, пожалуйста, даты начала и конца в формате гггг-мм-дд в <b>одном</b> сообщении через пробел!', parse_mode='html')
            bot.register_next_step_handler(msg, getting_a_response)
        except Exception:
            bot.send_message(message.chat.id, 'Ошибка отправки сообщения. Попробуйте позже.')


    def getting_a_response(message):
        message_from_user = str(message.text)

        if re.fullmatch(pattern, message_from_user):
            date_start, date_end = message_from_user.split(' ')

            if date_start <= date_end:
                URL_mytime = URL + str(date_start) + '/' + str(date_end) + '/'
                try:
                    response = requests.get(URL_mytime).json()
                except Exception:
                    bot.send_message(message.chat.id, f'Нет доступа к эндпоинту {URL}')
                response_str = str(response)
                bot.send_message(message.chat.id, response_str)
            else:
                msg = bot.send_message(message.chat.id, 'Дата начала не может быть больше даты окончания :)\nВведите корректные данные.')
                bot.register_next_step_handler(msg, getting_a_response)
        else:
            msg = bot.send_message(message.chat.id, 'Говорил же, дата нужна только формата ГГГГ-ММ-ДД. <b>Сначала начальная, потом, через пробел, конечная. Иначе никак не получится!</b>', parse_mode='html')
            bot.register_next_step_handler(msg, getting_a_response)


    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as err:
            print(err)
            time.sleep(RETRY_TIME)
