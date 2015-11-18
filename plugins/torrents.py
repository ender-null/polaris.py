# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *


commands = [
    '^torrent',
    '^t ',
    '^kickass'
]

parameters = {('query', True)}

description = 'Search Kickass Torrents. Results may be NSFW.'
action = 'typing'


def get_category_icon(category):
    if category == 'Anime':
        return u'🇯🇵'
    elif category == 'Applications':
        return u'📱'
    elif category == 'Books':
        return u'📖'
    elif category == 'Games':
        return u'🎮'
    elif category == 'Movies':
        return u'🎞'
    elif category == 'Music':
        return u'💽'
    elif category == 'TV':
        return u'🎞'
    elif category == 'XXX':
        return u'🔞'
    else:
        return u'❔'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://kat.cr/json.php'
    params = {
        'q': input
    }

    jdat = send_request(url, params)
    
    if not jdat:
        return send_error(msg, 'connection')

    if jdat['total_results'] == 0:
        return send_error(msg, 'results')

    limit = 6
    if len(jdat['total_results']) < limit:
        limit = len(jdat['total_results'])

    for v in jdat['list']:
        if v['seeds'] == 0:
            del v

    if len(jdat['list']) == 0:
        return send_error(msg, 'results')

    message = '*Kickass Search*: "_' + input + '_"\n\n'
    for i in range(0, limit):
        message += get_category_icon(jdat['list'][i]['category']) + ' [' + delete_markup(jdat['list'][i]['title']) + '](' + get_short_url(jdat['list'][i]['torrentLink']) + ')'
        if jdat['list'][i]['verified'] == 0:
            message += u' ❗️'
        size, unit = get_size(jdat['list'][i]['size'])
        message += '\n\t *' + size + ' ' + unit + 'B* | '

        size, unit = get_size(jdat['list'][i]['seeds'])
        message += '*' + size + unit + '* Seeds'

        size, unit = get_size(jdat['list'][i]['votes'])
        message += ' | ' + size + unit + u' 👍\n\n'

    message = message.replace('&amp;', '&')

    send_message(msg['chat']['id'], message, parse_mode="Markdown")
