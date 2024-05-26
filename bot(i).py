import telebot
from telebot import types
from config import *
import time
from db import *
# from yandex_gpt import *

# подготовка
bot = telebot.TeleBot(BOT_TOKEN)
create_database()
create_db_gtd()
create_db_kanban()
create_db_matrix()
create_db_reminder()
create_speech_gpt()

# кнопки
def buttons(task):
    print(task)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    for i in task:
        print(i)
        markup.add(i)
    return markup


markup_no = types.ReplyKeyboardRemove()

# меню и начало
@bot.message_handler(commands=['start'])
def handler_start(message):
    name = message.chat.first_name
    msg = bot.send_message(message.chat.id, f'<b>Привет, {name}\n</b>'
                                                 f'<i>я бот, в котором можно выбрать удобную\n'
                                                 f'систему планирования и контролировать свои задачи</i>', parse_mode='HTML', reply_markup=buttons(menu_list))
    bot.register_next_step_handler(msg, menu_go)


def menu(message):
    msg = bot.send_message(message.chat.id, f'<i>меню</i>',
                           parse_mode='html', reply_markup=buttons(menu_list))
    bot.register_next_step_handler(msg, menu_go)


def menu_go(message):
    if message.text == menu_list[0] or message.text == pomodoro_buttons[1]:
        msg = bot.send_message(message.chat.id, f'<i>Выбери систему планирования</i>',
                               parse_mode='html', reply_markup=buttons(Systems_plan))
        bot.register_next_step_handler(msg, change_plan)
    elif message.text == menu_list[2]:
        pomidoro_menu(message)
    elif message.text == menu_list[1]:
        pass


def change_plan(message):
    if message.text == Systems_plan[3]:
        pomidoro_menu(message)
    elif message.text == Systems_plan[2]:
        pass
        insert_database(message.chat.id, Systems_plan[2])
    elif message.text == Systems_plan[1]:
        insert_database(message.chat.id, Systems_plan[1])
        kanban_menu(message)
    elif message.text == Systems_plan[0]:
        insert_database(message.chat.id, Systems_plan[0])
        GTD_menu(message)
    elif message.text == Systems_plan[4]:
        menu(message)
    else:
        msg = bot.send_message(message.chat.id, f'<i>Выбери систему планирования</i>',
                               parse_mode='html', reply_markup=buttons(Systems_plan))
        bot.register_next_step_handler(msg, change_plan)


# GTD
def GTD_menu(message):
    msg = bot.send_message(message.chat.id, f'<i>Выбери, задачу на месяц или на неделю ты хочешь поставить (можешь переключаться между ними с помощью клавиатуры):</i>',
                           parse_mode='html', reply_markup=buttons(GTD_men))
    insert_gtd(message.chat.id, '', '')
    bot.register_next_step_handler(msg, GTD_go)


def GTD_go(message):
    if message.text == GTD_men[0]:
        msg = bot.send_message(message.chat.id, f'<i>Какова одна из задач на месяц?</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, insert_gtd_month_task)
    elif message.text == GTD_men[1]:
        msg = bot.send_message(message.chat.id, f'<i>Какова одна из задач на неделю?</i>',
                               parse_mode='html', reply_markup=markup_no)
        bot.register_next_step_handler(msg, insert_gtd_week_task)
    elif message.text == GTD_men[2]:
        gtd_plans(message)                     #########
    elif message.text == GTD_men[3]:
        gtd_plans(message)
    else:
        msg = bot.send_message(message.chat.id, f'<i>Поставь задачи на месяц или на неделю:</i>',
                               parse_mode='html', reply_markup=buttons(GTD_men))
        bot.register_next_step_handler(msg, GTD_go)


def insert_gtd_month_task(message):
    update_row_value_gtd(message.chat.id, 'main_task', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Чтобы ввести ещё одну задачу, нажми на "ещё".\n'
                           'Кнопка "назад" вернёт тебя в меню системы GTD </i>',
                           parse_mode='html', reply_markup=buttons(varies))
    bot.register_next_step_handler(msg, GTD_go)


def insert_gtd_week_task(message):
    update_row_value_gtd(message.chat.id, 'task', message.text)
    msg = bot.send_message(message.chat.id, f'<i>Чтобы ввести ещё одну задачу, нажми на "ещё".\n'
                           'Кнопка "назад" вернёт тебя в меню системы GTD </i>',
                           parse_mode='html', reply_markup=buttons(varies))
    bot.register_next_step_handler(msg, GTD_go)


def varies_handler(message):
    if message.text == varies[0]:
        bot.register_next_step_handler(message, GTD_go)
    elif message.text == varies[1]:
        bot.register_next_step_handler(message, GTD_go)


def gtd_plans(message):
    user_id = message.from_user.id
    gtd_messages = select_gtd(user_id)
    print(gtd_messages)
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
    elif message.text == kanban_men[4]:
        menu(message)
    elif message.text == kanban_men[3]:
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

def kanban_plans(message):
    user_id = message.from_user.id
    matrix_messages = select_matrix(user_id)
    s, m, g = matrix_messages
    bot.send_message(user_id,
                     f'Что сделано:\n{s}\nЧто делается:\n{m}\nЧто надо сделать:\n{g}')
    if s == '' and m == '' and g == '':
        bot.send_message(user_id, 'У вас пока что нет планов.')


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
    elif message.text == matrix_men[5]:
        menu(message)
    elif message.text == matrix_men[4]:
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
    bot.send_message(user_id, f'Важное срочное:\n{s}\nВажное несрочное:\n{m}\nНеважное срочное:\n{g}\nНеважное несрочное: {h}')
    if s == '' and m == '' and g == '' and h == '':
        bot.send_message(user_id, 'У вас пока что нет планов.')

# обучение
# def study_menu(message):
#     msg = bot.send_message(message.chat.id,
#                            f'Вы можете пройти мини-обучение по боту или спросить о планировании',
#                            parse_mode='html', reply_markup=buttons(study_men))
#     bot.register_next_step_handler(msg, study_go)

# def study_go(message):
#     if message.text == study_men[0]:
#         msg = bot.send_message(message.chat.id,
#                                f'Напишите свой вопрос',
#                                parse_mode='html')
#         bot.register_next_step_handler(msg, study_gpt)
#     elif message.text == study_men[1]:
#         study(message)
#     elif message.text == study_men[2]:
#         menu(message)

# def study(message):
#     msg = bot.send_message(message.chat.id, f'Поздравляем! Вы начали мини-обучение по системам планирования.',
#                            parse_mode='html', reply_markup=markup_no)
#     bot.register_next_step_handler(msg, study_GTD)


# def study_GTD(message):
#     msg = bot.send_message(message.chat.id, f'Getting Things Done, GTD - методика планирования, которая\n'
#                                             f'подразумевает постановку главной задачи, для достижения которой надо\n'
#                                             f'поставить более мелкие подзадачи, которые в случае надобности тоже могут\n'
#                                             f'разбиваться на подзадачи.',
#                            parse_mode='html', reply_markup=buttons(learning_men))

#     if message.text == learning_men[0]:
#         msg = bot.send_message(message.chat.id, f'https://singularity-app.ru/blog/gtd-in-singularityapp/\n'
#                                                 f'подробная статья о системе Getting Things Done',
#                                parse_mode='html', reply_markup=buttons(learning_men))
#     elif message.text == learning_men[1]:
#         msg = bot.send_photo(message.chat.id, f'blob:https://web.telegram.org/334b97ae-cb14-4596-bf5e-f48093e396ec',
#                                parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[2]:
#         msg = bot.send_message(message.chat.id, f'https://my.mail.ru/mail/qwerve/video/8/393.html\n'
#                                                 f'подробное видео о системе Getting Things Done',
#                                parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[3]:
#         bot.register_next_step_handler(msg, study_kanban)


# def study_kanban(message):
#     msg = bot.send_message(message.chat.id, f'Канбан — это методика управления проектами, которая\n'
#                                             f'представляет собой доску с разметкой — шагами проекта.\n'
#                                             f'На неё крепят карточки-задачи и перемещают их из этапа в этап\n'
#                                             f'по ходу работы.',
#                            parse_mode='html', reply_markup=buttons(learning_men))

#     if message.text == learning_men[0]:
#         msg = bot.send_message(message.chat.id, f'https://singularity-app.ru/blog/personalnyi-kanban/\n'
#                                                 f'подробная статья о системе Канбан',
#                                parse_mode='html', reply_markup=buttons(learning_men))
#     elif message.text == learning_men[1]:
#         msg = bot.send_photo(message.chat.id, f'https://avatars.dzeninfra.ru/get-zen_doc/1889358/pub_5fe21190785777679a4b8ea3_5fe23f12f7cdfe2e8961981d/scale_1200',
#                              parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[2]:
#         msg = bot.send_message(message.chat.id, f'https://youtu.be/M1-IcgdDJb0\n'
#                                                 f'подробное видео о системе Канбан',
#                                parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[3]:
#         bot.register_next_step_handler(msg, study_matrix)

# def study_matrix(message):
#     msg = bot.send_message(message.chat.id, f'Матрица Эйзенхауэра - это система, которая строится на том,\n'
#                                             f'что все дела делятся на 4 квадрата по параметрам срочности и важности.\n'
#                                             f'То есть формируются 4 списка дел:\n'
#                                             f'• важные несрочные\n'
#                                             f'• важные срочные\n'
#                                             f'• неважные срочные\n'
#                                             f'• неважные несрочные\n',
#                            parse_mode='html', reply_markup=buttons(learning_men))

#     if message.text == learning_men[0]:
#         msg = bot.send_message(message.chat.id, f'https://trends.rbc.ru/trends/education/60a519599a7947430a73ff6b\n'
#                                                 f'подробная статья о Матрице Эйзенхауэра',
#                                parse_mode='html', reply_markup=buttons(learning_men))
#     elif message.text == learning_men[1]:
#         msg = bot.send_photo(message.chat.id,
#                              f'https://3этаж.рф/800/600/http/new-world-rpg.ru/wp-content/uploads/4/5/b/45b10e439cb9e46701341bf3002f4b1d.jpeg',
#                              parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[2]:
#         msg = bot.send_message(message.chat.id, f'https://youtu.be/RmN3dDrJ1l4\n'
#                                                 f'подробное видео о Матрице Эйзенхауэра',
#                                parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[3]:
#         bot.register_next_step_handler(msg, study_pomodoro)


# def study_pomodoro(message):
#     msg = bot.send_message(message.chat.id, f'Система Помодоро направлена на максимальную концентрацию\n'
#                                             f'в определённый промежуток времени. Вы чередуете периоды интенсивной\n'
#                                             f'работы с периодами отдыха за счёт чего не "перегораете".\n'
#                                             f'Классически система настроена на 25 минут работы и 5 минут отдыха,\n'
#                                             f'и увеличенный интервал отдыха после нескольких циклов.\n',
#                            parse_mode='html', reply_markup=buttons(learning_men))

#     if message.text == learning_men[0]:
#         msg = bot.send_message(message.chat.id, f'https://trends.rbc.ru/trends/education/5f55e4ad9a79472e20842053\n'
#                                                 f'подробная статья о таймере Помодоро',
#                                parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[1]:
#         msg = bot.send_photo(message.chat.id,
#                              f'blob:https://web.telegram.org/9d6d3991-6358-407d-bb9c-a59cf41f7fa7',
#                              parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[2]:
#         msg = bot.send_message(message.chat.id, f'https://youtu.be/HfjcAiDrU6U\n'
#                                                 f'подробное видео о таймере Помодоро',
#                                parse_mode='html', reply_markup=buttons(learning_men))

#     elif message.text == learning_men[3]:
#         bot.register_next_step_handler(msg, study_menu)


# def study_gpt(message):
#     fil, ans, count = ask_gpt(message)
#     msg = bot.send_message(message.chat.id, ans, reply_markup=buttons(study_men))
#     bot.register_next_step_handler(msg, study_go)


# @bot.message_handler(content_types=['voice'])
# def voice_handler(message):
#     user_id = message.from_user.id
#     file_id = message.voice.file_id
#     file_info = bot.get_file(file_id)
#     file = bot.download_file(file_info.file_path)
#     stt_status, stt_text = stt(file)
#     if not stt_status:
#         """ если что-то не так, уведомляем пользователя """
#         bot.send_message(user_id, stt_text)
#         return
#     """ нужна функция в бд для добавления текста """
#     stt_blocks, error_message = count_all_limits(user_id, 'stt_blocks')
#     if not stt_blocks:
#         bot.send_message(user_id, error_message)
#         return
#     add_message(user_id=user_id, message=[stt_text, 'user', 0, 0, stt_blocks])


# @bot.message_handler(content_types=['voice'], text=['Вопрос к gpt'])
# def ask_gpt_with_voice(message):
#     user_id = message.from_user.id
#     last_message, spent_tokens = select_n_last_messages(user_id, 1)
#     total_gpt_tokens, error_message = count_all_limits(last_message, 'gpt_tokens')
#     if error_message:
#         bot.send_message(user_id, error_message)
#         return
#     status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_message)
#     if not status_gpt:
#         bot.send_message(user_id, answer_gpt)
#     tts_symbols, error_message = count_all_limits(message, 'tts_symbols')
#     add_message(user_id=user_id, message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])
#     if error_message:
#         bot.send_message(user_id, error_message)
#     bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
        
bot.polling(non_stop=True)