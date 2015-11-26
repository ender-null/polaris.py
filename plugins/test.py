# -*- coding: utf-8 -*-
from utilies import *
import bindings_cli as cli

commands = ['^test']
parameters = {('text', True)}
description = 'Repeat a string.'
#action = 'typing'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return cli.send_message(msg['chat']['id'], doc)

    cli.send_message(msg['chat']['id'], input)