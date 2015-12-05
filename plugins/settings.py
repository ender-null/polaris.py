# -*- coding: utf-8 -*-
from utilies import *

commands = [
    '^settings',
    '^nick'
]
description = 'Configure individual settings for the user.'
action = 'typing'

def run(msg):
    uid = str(msg['from']['id'])

    if get_command(msg['text']) == 'settings':
        message = '*Settings:*'
        for key in users[uid]:
            message += u'\n\t*{0}*: {1}'.format(key.title(), users[uid][key])
    
    elif get_command(msg['text']) == 'nick':
        input = get_input(msg['text'])
        if not input:
            return send_error(msg, 'argument')
        else:
            users[uid]['alias'] = input
            save_json('data/users.json', users)
            message = u'Starting from now I\'ll call you _{0}_.'.format(input)

    send_message(msg['chat']['id'], message, parse_mode="Markdown")

def process(msg):
    uid = str(msg['from']['id'])

    # Adds the user if not in database
    if not uid in users:
        users[uid] = OrderedDict()
        if 'username' in msg['from']:
            users[uid]['username'] = msg['from']['username']
        users[uid]['messages'] = 1
        save_json('data/users.json', users)
    else:
        users[uid]['messages'] += 1

    # Replaces user's name with the nick
    if 'alias' in users[uid]:
        msg['from']['first_name'] = users[uid]['alias']
        msg['from']['last_name'] = ''
        
        if ('reply_to_message' in msg and
            str(msg['reply_to_message']['from']['id']) == uid):
            msg['reply_to_message']['from']['first_name'] = users[uid]['alias']
            msg['reply_to_message']['from']['last_name'] = ''