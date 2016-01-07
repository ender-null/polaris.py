# -*- coding: utf-8 -*-
from utils import *


commands = ['^echo']
parameters = {('text', True)}
description = 'Repeat a string.'
action = 'typing'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    send_message(msg['chat']['id'], input, parse_mode="Markdown")

def inline(qry):
    input = get_input(qry['query'])

    results_json = []
    result = {
        'type': 'article',
        'id': first_word(input),
        'title': 'Echo',
        'message_text': input,
        'description': input,
        'thumb_url': 'http://fa2png.io/media/icons/fa-comment/96/16/673ab7_ffffff.png',
        'parse_mode': 'Markdown'
    }
    results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(qry['id'], results)
