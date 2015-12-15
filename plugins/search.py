# -*- coding: utf-8 -*-
from __main__ import *
from utils import *

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

    if msg['text'].startswith(config['command_start'] + 'insfw'):
        del params['safe']

    jstr = requests.get(
        url,
        params=params,
    )

    if jstr.status_code != 200:
        return send_error(msg, 'connection', jstr.status_code)

    jdat = json.loads(jstr.text)

    if jdat['responseData']['results'] < 1:
        return send_error(msg, 'results')

    text = '*Google Search*: "_' + input + '_"\n\n'
    for i in range(0, len(jdat['responseData']['results'])):
        result_url = jdat['responseData']['results'][i]['unescapedUrl']
        result_title = jdat['responseData']['results'][i]['titleNoFormatting']
        text += u'🌐 [' + delete_markup(result_title) + '](' + get_short_url(result_url) + ')\n\n'

    send_message(msg['chat']['id'], text, disable_web_page_preview=True, parse_mode="Markdown")
