# -*- coding: utf-8 -*-
from utilies import *

commands = [
    '^remindme',
    '^remind$',
    '^r '
]

parameters = (
    ('delay', True),
    ('message', True),
)

description = 'Set a reminder for yourself. First argument is the number of minutes until you wish to be reminded.'
action = 'typing'
hidden = True


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc,
                            parse_mode="Markdown")
    delay = first_word(input)
    
    message = all_but_first_word(input)
    if not message:
        send_message(msg['chat']['id'], 'Please include a reminder.')

def cron():
    pass
