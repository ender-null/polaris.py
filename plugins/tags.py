from core.utils import *
from core.bot import start

commands = [
    ('/tag', ['tags']),
    ('/remtag', ['tags'])
]
description = 'Well... you may guess it\'s used to tag stuff.'


def run(m):
    if not is_trusted(m.sender.id):
        return send_message(m, lang.errors.permission)

    input = get_input(m, ignore_reply=True)
    if not input:
        return send_message(m, lang.errors.input)

    if first_word(input).isdigit():
        uid = first_word(input)
        taglist = all_but_first_word(input).split()
    else:
        uid = str(m.reply.sender.id)
        taglist = input.split()

    message = lang.errors.id

    if get_command(m) == 'tag':
        if m.reply:
            message = '👤 %s\n🏷 ' % m.reply.sender.id
            for tag in taglist:
                message += set_tag(uid, tag)


    elif get_command(m) == 'remtag':
        taglist = input.split()
        if m.reply:
            message = '👤 %s\n🏷 ' % m.reply.sender.id
            uid = str(m.reply.sender.id)
            for tag in taglist:
                message += rem_tag(uid, tag)

    send_message(m, message, markup='HTML')
