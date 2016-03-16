from core.utils import *
from core.bot import start

commands = [
    ('/tag', ['tags']),
    ('/remtag', ['tags'])
]
description = 'Well... you may guess it\'s used to tag stuff.'
hidden = True


def run(m):
    if not is_trusted(m.sender.id):
        return send_message(m, lang.errors.permission)

    input = get_input(m, ignore_reply=True)
    if not input:
        return send_message(m, lang.errors.input)
        
    if m.reply:
        id = str(m.reply.sender.id)
    elif first_word(input) == '-g':
        id = str(m.receiver.id)
        input = all_but_first_word(input)
        print('tag for group: %s %s' % (id, input))
    elif first_word(input).isdigit():
        id = first_word(input)
        input = all_but_first_word(input)
    else:
        # id = str(m.sender.id)
        return send_message(m, lang.errors.id, markup='HTML')

    taglist = input.split()
    message = '👤 %s\n🏷 ' % id

    if get_command(m) == 'tag':
        for tag in taglist:
            message += set_tag(id, tag)


    elif get_command(m) == 'remtag':
        for tag in taglist:
            message += rem_tag(id, tag)

    send_message(m, message, markup='HTML')
