# -*- coding: utf-8 -*-
from utilies import *
import bindings_cli as cli

commands = ['^echotest', '^invitest', '^deletest']
parameters = {('text', True)}
description = 'Use it and I will kill you, twice.'
action = 'typing'
hidden = True

def run(msg):
    input = get_input(msg['text'])

    if get_command(msg['text']) == 'echotest':
        if not input:
            doc = get_doc(commands, parameters, description)
            return send_message(msg['chat']['id'], doc, parse_mode="Markdown")
        cli.send_message(msg['chat']['id'], input)

    elif get_command(msg['text']) == 'invitest':
        if 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
        else:
            if input.isdigit():
                user_id = input
            else:
                user_id = cli.user_id(input[1:])
        if not user_id:
            return send_error(msg, 'argument')
        print cli.chat_add_user(msg['chat']['id'], user_id)
        cli.chat_add_user(msg['chat']['id'], user_id)

    elif get_command(msg['text']) == 'deletest':
        if 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
        else:
            if input.isdigit():
                user_id = input
            else:
                user_id = cli.user_id(input[1:])
        if not user_id:
            return send_error(msg, 'argument')
            
        print cli.chat_del_user(msg['chat']['id'], user_id)
        cli.chat_del_user(msg['chat']['id'], user_id)