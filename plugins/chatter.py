from core.utils import *
from cleverbot import Cleverbot

commands = [
    ('^' + bot.username, [])
]
description = 'Repeat a string.'
hidden = True

def run(m):
    input = m.content.replace(bot.username + ' ', '')

    cb = Cleverbot()

    try:
        message = cb.ask(input)
    except:
        message = None

    send_message(m, message)

def process(m):
    if m.reply and m.type == 'text':
        if (m.reply.sender.id == bot.id and
                not m.content.startswith(config.start)):
            m.content = '@' + bot.username + ' ' + m.content

    if (m.type == 'text' and
        m.receiver.id > 0 and
        not m.content.startswith(config.start)):
        m.content = '@' + bot.username + ' ' + m.content