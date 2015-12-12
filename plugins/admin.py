# -*- coding: utf-8 -*-
from utilies import *
import subprocess
import sys

commands = [
    '^run ',
    '^reload',
    '^msg ',
    '^stop'
]

description = 'Get list of basic information for all commands, or more detailed documentation on a specified command.'
action = 'typing'
hidden = True


def run(msg):
    input = get_input(msg['text'])

    if not is_admin(msg):
        return send_error(msg, 'permission')

    if get_command(msg['text']) == 'run':
        message = '`{0}`'.format(subprocess.check_output(input, shell=True))

    elif get_command(msg['text']) == 'reload':
        bot_init()
        message = 'Bot reloaded!'

    elif get_command(msg['text']) == 'msg':
        chat_id = first_word(input)
        text = get_input(input)

        if not send_message(chat_id, text):
            return send_error(msg, 'argument')
        return

    elif get_command(msg['text']) == 'stop':
        is_started = False
        sys.exit()

    send_message(msg['chat']['id'], message, parse_mode="Markdown")
