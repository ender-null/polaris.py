# -*- coding: utf-8 -*-
from utils import *
from bs4 import BeautifulSoup


commands = [
    '^currency',
    '^cash',
    '^c '
]

parameters = (
    ('to', True),
    ('from', True),
    ('amount', False),
)

description = 'Convert an amount from one currency to another.'
action = 'typing'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc,
                            parse_mode="Markdown")

    from_currency = first_word(input).upper()
    to = first_word(input, 2).upper()
    amount = first_word(input, 3)

    if not int(amount):
        amount = 1
        result = 1

    if from_currency != to:
        url = 'http://www.google.com/finance/converter'
        params = {
            'from': from_currency,
            'to': to,
            'a': amount
        }

        jstr = requests.get(
            url,
            params=params,
        )

        if jstr.status_code != 200:
            return send_error(msg, 'connection', jstr.status_code)

        soup = BeautifulSoup(jstr.text, 'lxml')
        text = soup.find(class_='bld')
        
        if text:
            text = text.get_text()
            text = str(text).split()[0]
        else:
            return send_error(msg, 'results')
        result = text
    message = str(amount) + ' ' + from_currency + ' = *' + str(result) + ' ' + to + '*'
    send_message(msg['chat']['id'], message,
                 parse_mode="Markdown")
