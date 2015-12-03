# -*- coding: utf-8 -*-
from utilies import *
import random

commands = [
    '^define',
    '^ud',
    '^urbandictionary'
]

parameters = {('term', True)}
description = 'Returns the first definition for a given term from [Urban Dictionary](http://urbandictionary.com).'
action = 'typing'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://api.urbandictionary.com/v0/define'
    params = {'term': input}

    jdat = send_request(url, params)

    if not jdat:
        return send_error(msg, 'connection')

    if jdat['result_type'] == 'no_results':
        return send_error(msg, 'results')

    i = random.randint(1, len(jdat['list'])) - 1

    text = '*' + jdat['list'][i]['word'] + '*\n'
    text += jdat['list'][i]['definition'] + '\n'
    if jdat['list'][i]['example']:
        text += '\nExample:\n_' + jdat['list'][i]['example'] + '_'

    send_message(msg['chat']['id'], text, parse_mode="Markdown")
