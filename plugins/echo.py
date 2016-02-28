from core.utils import *

commands = [
    ('/echo', ['text'])
]
description = 'Repeat a string.'


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    send_message(m, input, markup ='Markdown', preview = False)
