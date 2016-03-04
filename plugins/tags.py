from core.utils import *
from core.bot import start

commands = [
    ('/tag', ['tag']),
    ('/remtag', ['tag'])
]
description = 'Well... you may guess it\'s used to tag stuff.'


def run(m):
    if not is_admin(m.sender.id):
        return send_message(m, lang.errors.permission)

    if not input:
        return send_message(m, lang.errors.input)

    message = lang.errors.argument

    if get_command(m) == 'tag':
        if 'reply' in m:
            if m.reply.sender.id in tags.list:
                message = 'found'
            else:
                message = 'not found'


    elif get_command(m) == 'remtag':
        pass

    send_message(m, message, markup='HTML')
