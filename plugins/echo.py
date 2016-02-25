from core.utils import *

commands = {
    '/echo': {('text', True)}
}
description = 'Repeat a string.'


def run(m):
    input = get_input(m)

    if not input:
        return send_msg(m, 'No input', markup = 'Markdown', preview=False)

    send_msg(m, input)
