# -*- coding: utf-8 -*-
from utils import *

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
            message += u'\n\t*{0}*: {1}'.format(key.title(), escape_markup(users[uid][key]))
    
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
        if 'username' in msg['from']:
            if not 'username' in users[uid]:
                users[uid]['username'] = msg['from']['username']

            if msg['from']['username'] != users[uid]['username']:
                users[uid]['username'] = msg['from']['username']
        else:
            if 'username' in users[uid]:
                del users[uid]['username']
        users[uid]['messages'] += 1

    # Replaces user's name with the nick
    if 'alias' in users[uid]:
        msg['from']['first_name'] = users[uid]['alias']
        msg['from']['last_name'] = ''
        
    if ('reply_to_message' in msg and
        str(msg['reply_to_message']['from']['id']) in users):
        uid = str(msg['reply_to_message']['from']['id'])
        if 'alias' in users[uid]:
            msg['reply_to_message']['from']['first_name'] = users[uid]['alias']
            msg['reply_to_message']['from']['last_name'] = ''
    elif ('new_chat_participant' in msg and
        str(msg['new_chat_participant']['id']) in users):
        uid = str(msg['new_chat_participant']['id'])
        if 'alias' in users[uid]:
            msg['new_chat_participant']['first_name'] = users[uid]['alias']
            msg['new_chat_participant']['last_name'] = ''
    elif ('left_chat_participant' in msg and
        str(msg['left_chat_participant']['id']) in users):
        uid = str(msg['left_chat_participant']['id'])
        if 'alias' in users[uid]:
            msg['left_chat_participant']['first_name'] = users[uid]['alias']
            msg['left_chat_participant']['last_name'] = ''
