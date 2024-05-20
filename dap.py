import telebot
from telebot import types
from bot import buttons, bot

gtd_buttons = ['новая', 'подзадача', 'конец']




def gtd(message):
    bot.send_message(message.chat.id, "Введите задачу", reply_markup= buttons(gtd_buttons))
    bot.register_next_step_handler(message, gtd_go)


def gtd_go(message):
    if message.text == gtd_buttons[0]:
        gtd(message)

def kanban(message):
    pass


Systems_plan = {'GTD': gtd, 'КАНБАН': kanban, 'МАТРИЦА ЭЙЗЕНХАУЭРА': ''}