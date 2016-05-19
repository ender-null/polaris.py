from core.utils import *

commands = [
    ('/echo', ['text']),
    ('/reverb', ['text'])
]
description = 'Repeat a string.'


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    if get_command(m) == 'reverb':
        preview = False
    else:
        preview = True
    
    text = input
    
    send_message(m, text, markup='Markdown', preview=preview)


def inline(m):
    input = get_input(m)
    if not input:
        input = lang.errors.input

    text = input

    fullwidth_text = fullwidth(text)
    quoted_fullwidth_text = fullwidth(text, True)

    if get_command(m) == 'reverb':
        preview = True
    else:
        preview = False


    results = [
        {
            'type': 'article',
            'id': '%s' % text,
            'title': 'No format',
            'message_text': text,
            'disable_web_page_preview': preview,
            'description': text,
            'thumb_url': 'http://fa2png.io/media/icons/icomoon-clear-formatting/96/32/ffffff_673ab7.png',
        },
        {
            'type': 'article',
            'id': '<b>%s</b>' % text,
            'title': 'Bold',
            'message_text': '<b>%s</b>' % text,
            'disable_web_page_preview': preview,
            'description': '*%s*' % text,
            'thumb_url': 'http://fa2png.io/media/icons/oi-bold/96/32/ffffff_673ab7.png',
            'parse_mode': 'HTML'
        },
        {
            'type': 'article',
            'id': '<i>%s</i>' % text,
            'title': 'Italic',
            'message_text': '<i>%s</i>' % text,
            'disable_web_page_preview': preview,
            'description': '_%s_' % text,
            'thumb_url': 'http://fa2png.io/media/icons/oi-italic/96/32/ffffff_673ab7.png',
            'parse_mode': 'HTML'
        },
        {
            'type': 'article',
            'id': '<pre>%s</pre>' % text,
            'title': 'Code',
            'message_text': '<pre>%s</pre>' % text,
            'disable_web_page_preview': preview,
            'description': '```%s```' % text,
            'thumb_url': 'http://fa2png.io/media/icons/oi-code/96/32/ffffff_673ab7.png',
            'parse_mode': 'HTML'
        },
        {
            'type': 'article',
            'id': fullwidth_text,
            'title': 'Ｆｕｌｌｗｉｄｔｈ',
            'message_text': fullwidth_text,
            'disable_web_page_preview': preview,
            'description': fullwidth_text,
            'thumb_url': 'http://i.imgur.com/GVVd8ek.png'
        },
        {
            'type': 'article',
            'id': quoted_fullwidth_text,
            'title': '﻿Ｆｕｌｌｗｉｄｔｈ  ｗｉｔｈ  ｑｕｏｔｅｓ',
            'message_text': quoted_fullwidth_text,
            'disable_web_page_preview': preview,
            'description': quoted_fullwidth_text,
            'thumb_url': 'http://i.imgur.com/FhgB10A.png'
        },
        {
            'type': 'article',
            'id': 'markdown:%s' % text,
            'title': 'Format with Markdown',
            'message_text': text,
            'disable_web_page_preview': preview,
            'description': text,
            'thumb_url': 'http://fa2png.io/media/icons/owi-markdown/96/32/ffffff_673ab7.png',
            'parse_mode': 'Markdown'
        },
        {
            'type': 'article',
            'id': 'html:%s' % text,
            'title': 'Format with HTML',
            'message_text': text,
            'disable_web_page_preview': preview,
            'description': input,
            'thumb_url': 'http://fa2png.io/media/icons/ion-social-html5-outline/96/32/ffffff_673ab7.png',
            'parse_mode': 'HTML'
        },
    ]

    answer_inline_query(m, results)
