import telebot
from telebot import types
from config import *
import time
from datetime import *
from db import *
from yandex_gpt import *
from speechkit import *
from multiprocessing import Process


# подготовка
bot = telebot.TeleBot(BOT_TOKEN)
create_database()
create_db_gtd()
create_db_kanban()
create_db_matrix()
create_db_reminder()


# кнопки
def buttons(task):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for i in task:
        markup.add(i)
    return markup


markup_no = types.ReplyKeyboardRemove()



#меню и начало
@bot.message_handler(commands=['start'])
def handler_start(message):
    insert_kanban(message.chat.id, '', '', '')
    insert_matrix(message.chat.id, '', '', '', '')
    name = message.chat.first_name
    msg = bot.send_message(message.chat.id, f'<b>Привет, {name}\n</b>'
                                                 f'<i>я бот, в котором можно выбрать удобную\n'
                                                 f'систему планирования и контролировать свои задачи</i>',
                                     parse_mode='html', reply_markup=buttons(men))
    bot.register_next_step_handler(msg, menu_go)


def menu(message):
    msg = bot.send_message(message.chat.id, f'<i>меню</i>',
                           parse_mode='html', reply_markup=buttons(men))
    bot.register_next_step_handler(msg, menu_go)


def menu_go(message):
    if message.text == men[0] or message.text == pomodoro_buttons[1]:
        msg = bot.send_message(message.chat.id, f'<i>Выбери систему планирования</i>',
                               parse_mode='html', reply_markup=buttons(Systems_plan))
        bot.register_next_step_handler(msg, change_plan)
    elif message.text == men[2]:
        pomidoro_menu(message)
    elif message.text == men[1]:
        pass


def change_plan(message):
    if message.text == Systems_plan[3]:
        pomidoro_menu(message)
    elif message.text == Systems_plan[2]:
        pass
        insert_database(message.chat.id, Systems_plan[2])
    elif message.text == Systems_plan[1]:
        kanban_menu(message)
        insert_database(message.chat.id, Systems_plan[1])
    elif message.text == Systems_plan[0]:
        GTD_menu(message)
        insert_database(message.chat.id, Systems_plan[0])
    elif message.text == Systems_plan[4]:
        menu(message)
    else:
        msg = bot.send_message(message.chat.id, f'<i>Выбери систему планирования</i>',
                               parse_mode='html', reply_markup=buttons(Systems_plan))
        bot.register_next_step_handler(msg, change_plan)

# Напоминалки
def reminder_menu(message):
    msg = bot.send_message(message.chat.id, 'Напишите текст или аудио для напоминалки',
                           parse_mode='html', reply_markup=buttons(reminder_men))
    bot.register_next_step_handler(msg, reminder_go)

def reminder_go(message):
    if message.text == reminder_men[0]:
        menu(message)
    else:
        if message.voice:
            ans = stt(message.voice)
            if ans[0]:
                msg = bot.send_message(message.chat.id, 'напишите время отпраки в формате:\n'
                                                        'день-месяц-год часы:минуты(по МСК(+3))'
                                                        'пример: 25-05-2024 15:30')
                bot.register_next_step_handler(msg, reminder_time, ans[1])
            else:
                msg = bot.send_message(message.chat.id, ans[1])
                bot.register_next_step_handler(msg, reminder_menu)
        else:
            msg = bot.send_message(message.chat.id, 'напишите время отпраки в формате:\n'
                                                    'день-месяц-год часы:минуты(по МСК(+3))'
                                                    'пример: 25-05-2024 15:30')
            bot.register_next_step_handler(msg, reminder_time, message.text)


def reminder_time(message, text):
    insert_reminder(message.chat.id, message.text, text)
    bot.send_message(message.chat.id, 'Напоминание сохранено)')
    menu(message)
# GTD
def GTD_menu(message):
    msg = bot.send_message(message.chat.id, f'<i>Поставь задачи на месяц или на неделю:</i>',
                           parse_mode='html', reply_markup=buttons(GTD_men))
    insert_gtd([message.chat.id, '', ''])
    bot.register_next_step_handler(msg, GTD_go)


def GTD_go(message):
    if message.text == GTD_men[0]:
        msg = bot.send_message(message.chat.id, f'<i>Какие задачи на месяц? (пиши по одной задаче)</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, insert_gtd_main_task)
    elif message.text == GTD_men[1]:
        msg = bot.send_message(message.chat.id, f'<i>Какие задачи на неделю? (пиши по одной задаче)</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, insert_gtd_task)
    elif message.text == GTD_men[2]:
        gtd_plans(message)
    elif message.text == GTD_men[3]:
        menu(message)
    else:
        msg = bot.send_message(message.chat.id, f'<i>Поставь задачи на месяц или на неделю:</i>',
                               parse_mode='html', reply_markup=buttons(GTD_men))
        bot.register_next_step_handler(msg, GTD_go)


def insert_gtd_main_task(message):
    update_row_value_gtd(message.chat.id, 'main_task', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи задачу на месяц:</i>',
                           parse_mode='html', reply_markup=buttons(GTD_men))
    bot.register_next_step_handler(msg, GTD_go)


def insert_gtd_task(message):
    update_row_value_gtd(message.chat.id, 'task', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи задачу на неделю:</i>',
                           parse_mode='html', reply_markup=buttons(GTD_men))
    bot.register_next_step_handler(msg, GTD_go)


def gtd_plans(message):
    user_id = message.from_user.id
    gtd_messages = select_gtd(user_id)
    s, m = gtd_messages
    bot.send_message(user_id, f'Задачи на месяц: {s}\nЗадачи на неделю: {m}')
    if s == '' and m == '':
        bot.send_message(user_id, 'У вас пока что нет планов.')


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
                                                f'кол-во циклов'
                                                f'Пример: 25 5 3</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, pomodoro_settings)

def pomodoro_settings(message):
    settings = [int(i) for i in str(message.text).split()]
    timer_pomidoro(message, job=settings[0], rest=settings[1], count=settings[2])


def timer_pomidoro(message, job=25, rest=5, count=3):
    offset = timedelta(hours=0)
    tz = timezone(offset, name='МСК')
    bot.send_message(message.chat.id, 'Пора работать')
    time = datetime.now(tz=tz)
    for _ in range(count):
        time += timedelta(minutes=job)
        time_str = time.strftime("%d-%m-%Y %H:%M")
        insert_reminder(message.chat.id, time_str, "Пора отдохнуть")
        time += timedelta(minutes=rest)
        time_str = time.strftime("%d-%m-%Y %H:%M")
        insert_reminder(message.chat.id, time_str, "Пора работать")




#Канбан
def kanban_menu(message): #
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                     parse_mode='html', reply_markup=buttons(kanban_men))
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
    elif message.text == kanban_men[4]:
        menu(message)
    elif message.text == kanban_men[3]:
        kanban_plans(message)
    else:
        msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                               parse_mode='html', reply_markup=buttons(kanban_men))
        bot.register_next_step_handler(msg, kanban_go)


def kanban_insert_done(message):
    if message.voice:
        ans = stt(message.voice)
        if ans[0]:
            update_row_value_kanban(message.chat.id, 'done', ans[1])
        else:
            msg = bot.send_message(message.chat.id, ans[1],
                                   parse_mode='html', reply_markup=buttons(kanban_men))
            bot.register_next_step_handler(msg, kanban_go)
    else:
        update_row_value_kanban(message.chat.id, 'done', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                           parse_mode='html', reply_markup=buttons(kanban_men))
    bot.register_next_step_handler(msg, kanban_go)


def kanban_insert_doing(message):
    if message.voice:
        ans = stt(message.voice)
        if ans[0]:
            update_row_value_kanban(message.chat.id, 'doing', ans[1])
        else:
            msg = bot.send_message(message.chat.id, ans[1],
                                   parse_mode='html', reply_markup=buttons(kanban_men))
            bot.register_next_step_handler(msg, kanban_go)
    else:
        update_row_value_kanban(message.chat.id, 'doing', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                           parse_mode='html', reply_markup=buttons(kanban_men))
    bot.register_next_step_handler(msg, kanban_go)


def kanban_insert_will_do(message):
    if message.voice:
        ans = stt(message.voice)
        if ans[0]:
            update_row_value_kanban(message.chat.id, 'will do', ans[1])
        else:
            msg = bot.send_message(message.chat.id, ans[1],
                                   parse_mode='html', reply_markup=buttons(kanban_men))
            bot.register_next_step_handler(msg, kanban_go)
    else:
        update_row_value_kanban(message.chat.id, 'will do', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Введи что сделано, что делается и что надо сделать:</i>',
                           parse_mode='html', reply_markup=buttons(kanban_men))
    bot.register_next_step_handler(msg, kanban_go)

def kanban_plans(message):
    user_id = message.from_user.id
    matrix_messages = select_kanban(user_id)
    s, m, g = matrix_messages[-1]
    bot.send_message(user_id,
                     f'Что сделано:\n{s}\nЧто делается:\n{m}\nЧто надо сделать:\n{g}')
    if s == '' and m == '' and g == '':
        bot.send_message(user_id, 'У вас пока что нет планов.')


# МАТРИЦА ЭЙЗЕНХАУЭРА
def matrix_menu(message):
    msg = bot.send_message(message.chat.id, f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                            parse_mode='html', reply_markup=buttons(matrix_men))
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
    elif message.text == matrix_men[5]:
        menu(message)
    elif message.text == matrix_men[4]:
        matrix_plans(message)
    else:
        msg = bot.send_message(message.chat.id, f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                               parse_mode='html', reply_markup=buttons(matrix_men))
        bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_imp_urg(message):
    if message.voice:
        ans = stt(message.voice)
        if ans[0]:
            update_row_value_kanban(message.chat.id, 'imp_urg', ans[1])
        else:
            msg = bot.send_message(message.chat.id, ans[1],
                                   parse_mode='html', reply_markup=buttons(matrix_men))
            bot.register_next_step_handler(msg, kanban_go)
    else:
        update_row_value_matrix(message.chat.id, 'imp_urg', message.text)
    msg = bot.send_message(message.chat.id, f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_imp_non_urg(message):
    if message.voice:
        ans = stt(message.voice)
        if ans[0]:
            update_row_value_kanban(message.chat.id, 'imp_nonur', ans[1])
        else:
            msg = bot.send_message(message.chat.id, ans[1],
                                   parse_mode='html', reply_markup=buttons(matrix_men))
            bot.register_next_step_handler(msg, kanban_go)
    else:
        update_row_value_matrix(message.chat.id, 'imp_nonur', message.text)
    msg = bot.send_message(message.chat.id,
                           f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_non_imp_urg(message):
    if message.voice:
        ans = stt(message.voice)
        if ans[0]:
            update_row_value_kanban(message.chat.id, 'unimp_urg', ans[1])
        else:
            msg = bot.send_message(message.chat.id, ans[1],
                                   parse_mode='html', reply_markup=buttons(matrix_men))
            bot.register_next_step_handler(msg, kanban_go)
    else:
        update_row_value_matrix(message.chat.id, 'unimp_urg', message.text)
    msg = bot.send_message(message.chat.id,
                           f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_insert_non_imp_non_urg(message):
    if message.voice:
        ans = stt(message.voice)
        if ans[0]:
            update_row_value_kanban(message.chat.id, 'unimp_nonurg', ans[1])
        else:
            msg = bot.send_message(message.chat.id, ans[1],
                                   parse_mode='html', reply_markup=buttons(matrix_men))
            bot.register_next_step_handler(msg, kanban_go)
    else:
        update_row_value_matrix(message.chat.id, 'unimp_nonurg', message.text)
    msg = bot.send_message(message.chat.id,
                           f'Введите задачи: важные срочные, важные несрочные, неважные срочные, неважные несрочные.',
                           parse_mode='html', reply_markup=buttons(matrix_men))
    bot.register_next_step_handler(msg, matrix_go)


def matrix_plans(message):
    user_id = message.from_user.id
    matrix_messages = select_matrix(user_id)
    s, m, g, h = matrix_messages
    bot.send_message(user_id, f'Важное срочное:\n{s}\nВажное несрочное:\n{m}\nНеважное срочное:\n{g}\nНеважное несрочное: {h}')
    if s == '' and m == '' and g == '' and h == '':
        bot.send_message(user_id, 'У вас пока что нет планов.')

# обучение
def study_menu(message):
    msg = bot.send_message(message.chat.id,
                           f'Вы можете пройти мини-обучение по боту или спросить о планировании',
                           parse_mode='html', reply_markup=buttons(study_men))
    bot.register_next_step_handler(msg, study_go)

def study_go(message):
    if message.text == study_men[0]:
        msg = bot.send_message(message.chat.id,
                               f'Напишите свой вопрос',
                               parse_mode='html')
        bot.register_next_step_handler(msg, study_gpt)
    elif message.text == study_men[1]:
        study(message)
    elif message.text == study_men[2]:
        menu(message)

def study(message):
    msg = bot.send_message(message.chat.id, f'Поздравляем! Вы начали мини-обучение по системам планирования.',
                           parse_mode='html', reply_markup=markup_no)
    bot.register_next_step_handler(msg, study_GTD)


def study_GTD(message):
    msg = bot.send_message(message.chat.id, f'Getting Things Done, GTD - методика планирования, которая\n'
                                            f'подразумевает постановку главной задачи, для достижения которой надо\n'
                                            f'поставить более мелкие подзадачи, которые в случае надобности тоже могут\n'
                                            f'разбиваться на подзадачи.',
                           parse_mode='html', reply_markup=buttons(learning_men))

    if message.text == learning_men[0]:
        msg = bot.send_message(message.chat.id, f'https://singularity-app.ru/blog/gtd-in-singularityapp/\n'
                                                f'подробная статья о системе Getting Things Done',
                               parse_mode='html', reply_markup=buttons(learning_men))
    elif message.text == learning_men[1]:
        msg = bot.send_photo(message.chat.id, f'blob:https://web.telegram.org/334b97ae-cb14-4596-bf5e-f48093e396ec',
                               parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[2]:
        msg = bot.send_message(message.chat.id, f'https://my.mail.ru/mail/qwerve/video/8/393.html\n'
                                                f'подробное видео о системе Getting Things Done',
                               parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[3]:
        bot.register_next_step_handler(msg, study_kanban)


def study_kanban(message):
    msg = bot.send_message(message.chat.id, f'Канбан — это методика управления проектами, которая\n'
                                            f'представляет собой доску с разметкой — шагами проекта.\n'
                                            f'На неё крепят карточки-задачи и перемещают их из этапа в этап\n'
                                            f'по ходу работы.',
                           parse_mode='html', reply_markup=buttons(learning_men))

    if message.text == learning_men[0]:
        msg = bot.send_message(message.chat.id, f'https://singularity-app.ru/blog/personalnyi-kanban/\n'
                                                f'подробная статья о системе Канбан',
                               parse_mode='html', reply_markup=buttons(learning_men))
    elif message.text == learning_men[1]:
        msg = bot.send_photo(message.chat.id, f'https://avatars.dzeninfra.ru/get-zen_doc/1889358/pub_5fe21190785777679a4b8ea3_5fe23f12f7cdfe2e8961981d/scale_1200',
                             parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[2]:
        msg = bot.send_message(message.chat.id, f'https://youtu.be/M1-IcgdDJb0\n'
                                                f'подробное видео о системе Канбан',
                               parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[3]:
        bot.register_next_step_handler(msg, study_matrix)

def study_matrix(message):
    msg = bot.send_message(message.chat.id, f'Матрица Эйзенхауэра - это система, которая строится на том,\n'
                                            f'что все дела делятся на 4 квадрата по параметрам срочности и важности.\n'
                                            f'То есть формируются 4 списка дел:\n'
                                            f'• важные несрочные\n'
                                            f'• важные срочные\n'
                                            f'• неважные срочные\n'
                                            f'• неважные несрочные\n',
                           parse_mode='html', reply_markup=buttons(learning_men))

    if message.text == learning_men[0]:
        msg = bot.send_message(message.chat.id, f'https://trends.rbc.ru/trends/education/60a519599a7947430a73ff6b\n'
                                                f'подробная статья о Матрице Эйзенхауэра',
                               parse_mode='html', reply_markup=buttons(learning_men))
    elif message.text == learning_men[1]:
        msg = bot.send_photo(message.chat.id,
                             f'https://3этаж.рф/800/600/http/new-world-rpg.ru/wp-content/uploads/4/5/b/45b10e439cb9e46701341bf3002f4b1d.jpeg',
                             parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[2]:
        msg = bot.send_message(message.chat.id, f'https://youtu.be/RmN3dDrJ1l4\n'
                                                f'подробное видео о Матрице Эйзенхауэра',
                               parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[3]:
        bot.register_next_step_handler(msg, study_pomodoro)


def study_pomodoro(message):
    msg = bot.send_message(message.chat.id, f'Система Помодоро направлена на максимальную концентрацию\n'
                                            f'в определённый промежуток времени. Вы чередуете периоды интенсивной\n'
                                            f'работы с периодами отдыха за счёт чего не "перегораете".\n'
                                            f'Классически система настроена на 25 минут работы и 5 минут отдыха,\n'
                                            f'и увеличенный интервал отдыха после нескольких циклов.\n',
                           parse_mode='html', reply_markup=buttons(learning_men))

    if message.text == learning_men[0]:
        msg = bot.send_message(message.chat.id, f'https://trends.rbc.ru/trends/education/5f55e4ad9a79472e20842053\n'
                                                f'подробная статья о таймере Помодоро',
                               parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[1]:
        msg = bot.send_photo(message.chat.id,
                             f'blob:https://web.telegram.org/9d6d3991-6358-407d-bb9c-a59cf41f7fa7',
                             parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[2]:
        msg = bot.send_message(message.chat.id, f'https://youtu.be/HfjcAiDrU6U\n'
                                                f'подробное видео о таймере Помодоро',
                               parse_mode='html', reply_markup=buttons(learning_men))

    elif message.text == learning_men[3]:
        bot.register_next_step_handler(msg, study_menu)


def study_gpt(message):
    fil, ans, count = ask_gpt(message)
    msg = bot.send_message(message.chat.id, ans, reply_markup=buttons(study_men))
    bot.register_next_step_handler(msg, study_go)


def reminder_check():
    offset = timedelta(hours=3)
    tz = timezone(offset, name='МСК')
    time = datetime.now(tz=tz)
    time_str = time.strftime("%d-%m-%Y %H:%M")
    msg_task = its_time(time_str)
    for i in msg_task:
        bot.send_message(i[0], i[2])

if __name__ == '__main__':
    p = Process(target=reminder_check)
    p.start()
    p.join()

bot.polling()
