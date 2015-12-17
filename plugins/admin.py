# -*- coding: utf-8 -*-
from utils import *
import subprocess
import sys

commands = [
    '^run',
    '^msg',
    '^reload',
    '^stop',
    '^tag'
]
action = 'typing'
hidden = True


def run(msg):
    if not is_admin(msg):
        return send_error(msg, 'permission')

    input = get_input(msg['text'])

    if get_command(msg['text']) == 'run':
        if not input:
            return send_error(msg, 'argument')
        message = '`{0}`'.format(subprocess.getoutput(input))

    elif get_command(msg['text']) == 'msg':
        if not input:
            return send_error(msg, 'argument')
        chat_id = first_word(input)
        text = get_input(input)

        if not send_message(chat_id, text):
            return send_error(msg, 'argument')
        return

    elif get_command(msg['text']) == 'reload':
        bot_init()
        message = 'Bot reloaded!'

    elif get_command(msg['text']) == 'stop':
        is_started = False
        sys.exit()
    elif get_command(msg['text']) == 'tag':
        if not input:
            return send_error(msg, 'argument')
        tags = first_word(input).split('+')
        uid = all_but_first_word(input)
        if uid:
            uid = uid.split()

        if 'reply_to_message' in msg:
            uid = str(msg['reply_to_message']['from']['id'])
        
        if 'alias' in users[uid]:
            name = users[uid]['alias']
        elif 'username' in users[uid]:
            name = users[uid]['username']
        else:
            name = uid


        message = '👤 *' + name + '*\n🏷 '
        if 'tags' in users[uid]:
            for tag in tags:
                if not tag in users[uid]:
                    message += tag + ' '
                    users[uid]['tags'].append(tag)
        else:
            users[uid]['tags'] = []
            for tag in tags:
                if not tag in users[uid]:
                    message += tag + ' '
                    users[uid]['tags'].append(tag)
        save_json('data/users.json', users)

    send_message(msg['chat']['id'], message, parse_mode="Markdown")
