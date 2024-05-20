import telebot
from telebot import types
from config import *


bot = telebot.TeleBot(BOT_TOKEN)

def buttons(task):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for i in task:
        markup.add(i)
    return markup


markup_no = types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start'])
def handler_start(message):
    name = message.chat.first_name
    msg = bot.send_message(message.chat.id, f'<b>Привет, {name}\n</b>'
                                                      f'<i>я бот, в котором можно выбрать удобную\n'
                                                      f'систему планирования и контролировать свои задачи</i>',
                                     parse_mode='html', reply_markup=buttons(menu))
    bot.register_next_step_handler(msg, menu_go)


def menu_go(message):
    pass