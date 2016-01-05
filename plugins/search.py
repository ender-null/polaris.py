# -*- coding: utf-8 -*-
from __main__ import *
from bs4 import BeautifulSoup

from utils import *
from hashlib import md5

commands = [
    '^search',
    '^google',
    '^g ',
    '^gnswf'
]

parameters = {('query', True)}

description = 'This command performs a Google search for the given query. Safe search is enabled by default; use *' + config['command_start'] + 'gnsfw* to get potentially NSFW results.'
action = 'typing'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://ajax.googleapis.com/ajax/services/search/web'
    params = {
        'v': '1.0',
        'rsz': 6,
        'safe': 'active',
        'q': input
    }

    if msg['text'].startswith(config['command_start'] + 'gnsfw'):
        del params['safe']

    jstr = requests.get(
        url,
        params=params,
    )

    if jstr.status_code != 200:
        return send_error(msg, 'connection', jstr.status_code)

    jdat = json.loads(jstr.text)

    if len(jdat['responseData']['results']) < 1:
        return send_error(msg, 'results')

    text = '*Google Search*: "_' + input + '_"\n\n'
    for i in range(0, len(jdat['responseData']['results'])):
        result_url = jdat['responseData']['results'][i]['unescapedUrl']
        result_title = jdat['responseData']['results'][i]['titleNoFormatting']
        text += u'🌐 [' + escape_markup(result_title) + '](' + get_short_url(result_url) + ')\n\n'

    send_message(msg['chat']['id'], text, disable_web_page_preview=True, parse_mode="Markdown")


def inline(qry):
    input = get_input(qry['query'])

    url = 'http://ajax.googleapis.com/ajax/services/search/web'
    params = {
        'v': '1.0',
        'rsz': 8,
        'safe': 'active',
        'q': input
    }
    if first_word(qry['query']) == 'gnsfw':
        del params['safe']

    jdat = send_request(url, params)

    results_json = []
    i = 0
    for item in jdat['responseData']['results']:
        result = {
            'type': 'article',
            'id': str(i),
            'title': item['titleNoFormatting'],
            'message_text': item['unescapedUrl'],
            'description': BeautifulSoup(item['content'], 'lxml').text,
            'url': item['unescapedUrl'],
            'thumb_url': 'http://fa2png.io/media/icons/fa-globe/96/16/673ab7_ffffff.png',
            'thumb_width': 128,
            'thumb_height': 128
        }
        results_json.append(result)
        i += 1

    results = json.dumps(results_json)
    answer_inline_query(qry['id'], results)
