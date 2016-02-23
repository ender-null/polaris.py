from core.shared import *
from core.utils import *

commands = {
    '/echo': {('text', True)}
}
description = 'Repeat a string.'


def run(m):
    input = get_input(m.content)

    if not input:
        return send_msg(m, 'No input')

    send_msg(m, input)
