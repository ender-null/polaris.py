# -*- coding: utf-8 -*-
from utils import *
from bs4 import BeautifulSoup


commands = [
    '^adv',
    '^ascodevida'
]

description = 'Returns a random Hot Sick, Rude, Offensive & Politically Incorrect joke from [Sickipedia](http://sickipedia.org).'
action = 'typing'
hidden = True


def run(msg):
    url = 'http://www.ascodevida.com/aleatorio'

    jstr = requests.get(url)

    if jstr.status_code != 200:
        return send_error(msg, 'connection')

    soup = BeautifulSoup(jstr.text, 'lxml')

    text = soup.find(class_='advlink').get_text()
    text = text.replace('<br/>', '\n')
    text = text.replace('\t', '')

    send_message(msg['chat']['id'], text, parse_mode="Markdown")
