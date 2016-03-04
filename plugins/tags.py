from core.utils import *
from core.bot import start

commands = [
    ('/tag', ['tags']),
    ('/remtag', ['tags'])
]
description = 'Well... you may guess it\'s used to tag stuff.'


def run(m):
    if not is_admin(m.sender.id):
        return send_message(m, lang.errors.permission)
    
    input = get_input(m, ignore_reply=True)
    if not input:
        return send_message(m, lang.errors.input)

    message = lang.errors.id

    if get_command(m) == 'tag':
        taglist = input.split()
        if m.reply:
            message = '👤 %s\n🏷 ' % (m.reply.sender.id)
            uid = str(m.reply.sender.id)
            if uid in tags.list:
                for tag in taglist:
                    tags.list[uid].append(tag)
                    message += tag + ' '
            else:
                for tag in taglist:
                    tags.list[uid] = [tag]
                    message += '\'%s\' ' % (tag)

            tags.save(tags)
            


    elif get_command(m) == 'remtag':
        taglist = input.split()
        if m.reply:
            message = '👤 %s\n🏷 ' % (m.reply.sender.id)
            uid = str(m.reply.sender.id)
            if uid in tags.list:
                for tag in taglist:
                    if tag in tags.list[uid]:
                        tags.list[uid].remove(tag)
                        message += '-\'%s\' ' % (tag)
            else:
                message = '%s doesn\'t have any tag yet.' % m.reply.sender.first_name

            tags.save(tags)

    send_message(m, message, markup='HTML')
