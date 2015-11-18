# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *


commands = ['^who', '^whoami']

description = 'Gets user info.'
action = 'typing'


def run(msg):

    if 'reply_to_message' in msg:
        msg['from'] = msg['reply_to_message']['from']
        msg['chat'] = msg['reply_to_message']['chat']

    message = '#GREETING!\n'
    if msg['from']['id'] != bot['id']:
        message += 'You\'re *' + escape_markup(msg['from']['first_name']) + '*! '
    message += 'I\'m *#BOT_FIRSTNAME*.\n'
    message += 'Nice to meet you.\n\n'
    if msg['from']['username']:
        message += '*Username*: @' + escape_markup(msg['from']['username']) + '\n'
    message += '*User ID*: ' + str(msg['from']['id']) + '\n'
    if msg['chat']['type'] == 'group':
        #message += '*Group*: ' + escape_markup(msg['chat']['title']) + '\n'
        message += '*Group ID*: ' + str(msg['chat']['id']) + ''

    message = tag_replace(message, msg)

    send_message(msg['chat']['id'], message, parse_mode="Markdown")
