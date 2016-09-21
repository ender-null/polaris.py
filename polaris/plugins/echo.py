from polaris.bindings import send_message
from polaris.utils import get_input

commands = {
    '/echo': {
        'text': True
    }
}
description = 'Repeat a string.'


def run(bot, m):
    input = get_input(m)

    if not input:
        return send_message(bot, m, 'Need input')
    
    send_message(bot, m, input, markup='Markdown')
        
