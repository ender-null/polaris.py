# -*- coding: utf-8 -*-
from utilies import *


commands = ['^echo']
parameters = (('text', True))
description = 'Repeat a string.'
action = 'typing'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    send_message(msg['chat']['id'], input, parse_mode="Markdown")
