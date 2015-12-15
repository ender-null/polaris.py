# -*- coding: utf-8 -*-
from __main__ import *
from utils import *


commands = [
    '^wikipedia',
    '^wiki'
]

parameters = {('topic', True)}

description = 'Search Wikipedia for a relevant article and return its summary.'
action = 'typing'
hidden = True


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://ajax.googleapis.com/ajax/services/search/web'
    params = {
        'v': '1.0',
        'rsz': 1,
        'q': 'site:wikipedia.org ' + input
    }

    jstr = requests.get(
        url,
        params=params,
    )

    if jstr.status_code != 200:
        return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['connection'].format(jstr.status_code), parse_mode="Markdown")

    title_data = json.loads(jstr.text)
    wiki_url = title_data.responseData.results[1].url
    wiki_title = title_data.responseData.results[1].titleNoFormatting
    wiki_title = wiki_title.replace(' %- Wikipedia, the free encyclopedia', '')

    wiki_url = 'http://en.wikipedia.org/w/api.php'
    wiki_params = {
        'action': 'query',
        'prop': 'extracts',
        'format': 'json',
        'exchars': '4000',
        'exsectionformat': 'plain',
        'titles': wiki_title
    }

    jstr = requests.get(
        wiki_url,
        params=wiki_params,
    )

    if jstr.status_code != 200:
        return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['connection'].format(jstr.status_code), parse_mode="Markdown")

    text = json.loads(jstr.text)['query']['pages']
    for v in text:
        text = v
        break

    text = text + '\n' + wiki_url

    send_message(msg['chat']['id'], text, parse_mode="Markdown")
