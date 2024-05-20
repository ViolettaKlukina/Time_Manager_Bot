import telebot
from telebot import types
from config import BOT_TOKEN
from dap import *


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
    bot.send_message(message.chat.id, f'<b>Привет, {name}\n</b>'
                                                      f'<i>Я Бот, в котором можно выбрать\n'
                                                      f'удобную систему планирования и\n'
                                                      f'контролировать свои задачи</i>',
                                     parse_mode='html', reply_markup=buttons(["/plan", "/plan_add"]))

@bot.message_handler(commands=['/plan_add'])
def add_plan(message):
    name = message.chat.first_name
    bot.send_message(message.chat.id, "Выберите систему планирования)", reply_markup=buttons(Systems_plan.keys()))
    bot.register_next_step_handler(message, adding)

def adding(message):
    if message not in Systems_plan.keys():
        bot.send_message(message.chat.id, 'Выберите корректный ответ')
        bot.register_next_step_handler(message, adding)
    else:
        if