import telebot
from telebot import types
from config import *
import time
from db import *

#подготовка
bot = telebot.TeleBot(BOT_TOKEN)
create_database()
create_db_gtd()
create_db_kanban()
create_db_matrix()
create_db_reminder()


#кнопки
def buttons(task):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for i in task:
        markup.add(i)
    return markup


markup_no = types.ReplyKeyboardRemove()

#меню и начало
@bot.message_handler(commands=['start'])
def handler_start(message):
    name = message.chat.first_name
    msg = bot.send_message(message.chat.id, f'<b>Привет, {name}\n</b>'
                                                      f'<i>я бот, в котором можно выбрать удобную\n'
                                                      f'систему планирования и контролировать свои задачи</i>',
                                     parse_mode='html', reply_markup=buttons(menu))
    bot.register_next_step_handler(msg, menu_go)

def menu(message):
    msg = bot.send_message(message.chat.id, f'<i>меню</i>',
                           parse_mode='html', reply_markup=buttons(menu))
    bot.register_next_step_handler(msg, menu_go)


def menu_go(message):
    if message.text == menu[0] or message.text == pomodoro_buttons[1]:
        msg = bot.send_message(message.chat.id, f'<i>Выбери систему планирования</i>',
                               parse_mode='html', reply_markup=buttons(Systems_plan))
        bot.register_next_step_handler(msg, change_plan)
    elif message.text == menu[2]:
        pomidoro_menu(message)
    elif message.text == menu[1]:
        pass


def change_plan(message):
    if message.text == Systems_plan[3]:
        pomidoro_menu(message)
    elif message.text == Systems_plan[2]:
        pass
    elif message.text == Systems_plan[1]:
        kanban_menu(message)
    elif message.text == Systems_plan[0]:
        pass# путь в часть GTD
    elif message.text == Systems_plan[4]:
        menu(message)
    else:
        msg = bot.send_message(message.chat.id, f'<i>Выбери систему планирования</i>',
                               parse_mode='html', reply_markup=buttons(Systems_plan))
        bot.register_next_step_handler(msg, change_plan)

# GTD
#Вета можешь здесь писать


#POMODORO
def pomidoro_menu(message):
    msg = bot.send_message(message.chat.id, f'<i>поумолчанию 25 минут работы, 5 минут отдыха, 3 цикла</i>',
                           parse_mode='html', reply_markup=buttons(pomodoro_buttons))
    bot.register_next_step_handler(msg, pomodoro_go)

def pomodoro_go(message):
    if message.text == pomodoro_buttons[0]:
        timer_pomidoro(message)
    elif message.text == pomodoro_buttons[1]:
        menu_go(message)
    elif message.text == pomodoro_buttons[2]:
        msg = bot.send_message(message.chat.id, f'<i>напишите числа через пробел и начнётся таймер:'
                                                f'кол-во минут работы'
                                                f'кол-во минут отдыха в первый цикл'
                                                f'кол-во циклов</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, pomodoro_settings)

def pomodoro_settings(message):
    settings = [int(i) for i in str(message.text).split()]
    timer_pomidoro(message, job=settings[0], rest=settings[1], count=settings[2])


def timer_pomidoro(message, job=25, rest=5, count=3):
    for i in range(count):
        bot.send_message(message.chat.id, f'<i>Пора работать</i>', parse_mode='html')
        time.sleep(60 * job)
        if i != count - 1:
            bot.send_message(message.chat.id, f'<i>пора отдохнуть</i>', parse_mode='html')
            time.sleep(60 * (rest + i * 3))
    menu(message)

#Канбан
def kanban_menu(message): #
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                     parse_mode='html', reply_markup=buttons(kanban_men))
    insert_kanban([message.chat.id, '', '', ''])
    bot.register_next_step_handler(msg, kanban_go)

def kanban_go(message):
    if message.text == kanban_men[0]:
        msg = bot.send_message(message.chat.id, f'<i>что сделано?</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, kanban_insert_done)
    elif message.text == kanban_men[1]:
        msg = bot.send_message(message.chat.id, f'<i>что делается?</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, kanban_insert_doing)
    elif message.text == kanban_men[2]:
        msg = bot.send_message(message.chat.id, f'<i>что надо сделать?</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, kanban_insert_will_do)
    elif message.text == kanban_men[3]:
        menu(message)
    elif message.text == kanban_men[4]:
        kanban_plans(message)
    else:
        msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                               parse_mode='html', reply_markup=buttons(kanban_men))
        bot.register_next_step_handler(msg, kanban_go)


def kanban_insert_done(message):
    update_row_value_kanban(message.chat.id, 'done', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                           parse_mode='html', reply_markup=buttons(kanban_men))
    bot.register_next_step_handler(msg, kanban_go)


def kanban_insert_doing(message):
    update_row_value_kanban(message.chat.id, 'doing', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                           parse_mode='html', reply_markup=buttons(kanban_men))
    bot.register_next_step_handler(msg, kanban_go)


def kanban_insert_will_do(message):
    update_row_value_kanban(message.chat.id, 'will do', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                           parse_mode='html', reply_markup=buttons(kanban_men))
    bot.register_next_step_handler(msg, kanban_go)

def kanban_insert_done(message):
    update_row_value_kanban(message.chat.id, 'done', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                           parse_mode='html', reply_markup=buttons(kanban_men))
    bot.register_next_step_handler(msg, kanban_go)


# МАТРИЦА ЭЙЗЕНХАУЭРА
def matrix_menu(message):
    msg = bot.send_message(message.chat.id, f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                            parse_mode='html', reply_markup=buttons(matrix_men))
    insert_matrix([message.chat.id, '', '', '', ''])
    bot.register_next_step_handler(msg, matrix_go)


def matrix_go(message):
    if message.text == matrix_men[0]:
        msg = bot.send_message(message.chat.id, f'Какие у вас есть важные срочные задачи?',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, matrix_insert_imp_urg)
    elif message.text == matrix_men[1]:
        msg = bot.send_message(message.chat.id, f'Какие у вас есть важные несрочные задачи?',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, matrix_insert_imp_non_urg)
    elif message.text == matrix_men[2]:
        msg = bot.send_message(message.chat.id, f'Какие у вас есть неважные срочные задачи?',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, matrix_insert_non_imp_urg)
    elif message.text == matrix_men[3]:
        msg = bot.send_message(message.chat.id, f'Какие у вас неважные несрочные задачи?',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, matrix_insert_non_imp_non_urg)
    elif message.text == matrix_men[4]:
        menu(message)
    elif message.text == matrix_men[5]:
        matrix_plans(message)
    else:
        msg = bot.send_message(message.chat.id, f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                               parse_mode='html', reply_markup=buttons(matrix_men))
        bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_imp_urg(message):
    update_row_value_matrix(message.chat.id, 'imp_urg', message.text)
    msg = bot.send_message(message.chat.id, f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_imp_non_urg(message):
    update_row_value_matrix(message.chat.id, 'imp_nonur', message.text)
    msg = bot.send_message(message.chat.id,
                           f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_non_imp_urg(message):
    update_row_value_matrix(message.chat.id, 'unimp_urg', message.text)
    msg = bot.send_message(message.chat.id,
                           f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_non_imp_non_urg(message):
    update_row_value_matrix(message.chat.id, 'unimp_urg', message.text)
    msg = bot.send_message(message.chat.id,
                           f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_plans(message):
    user_id = message.from_user.id
    matrix_messages = select_matrix(user_id)
    s, m, g, h = matrix_messages
    bot.send_message(user_id, f'Важное срочное: {s}\nВажное несрочное: {m}\nНеважное срочное: {g}\nНеважное несрочное: {h}')
