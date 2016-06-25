from core.utils import *
from random import randint
from re import search

commands = [
    ('/roulette', [])
]
description = 'Russian roulette!'

def run(m):
    uid = m.sender.id
    gid = m.receiver.id

    if gid > 0:
        return send_message(m, lang.errors.notgroup, markup='HTML')

    bullets = None

    if has_tag(gid, 'roulette:?'):
        for tag in tags.list[str(gid)]:
            if tag.startswith('roulette:'):
                bullets = int(tag.split(':')[1])

    if not bullets:
        bullets = 6
        set_tag(m.receiver.id, 'roulette:' + str(bullets))
    
    if randint(0, bullets) == 0:
        rem_tag(m.receiver.id, 'roulette:' + str(bullets))
        bullets = 6
        set_tag(m.receiver.id, 'roulette:' + str(bullets))

        res = kick_user(m, uid)
        unban_user(m, uid)

        if res is None:
            return send_message(m, lang.errors.notchatadmin, markup='HTML')
        elif not res:
            return send_message(m, lang.errors.failed, markup='HTML')
        else:
            return send_message(m, '<b>%s</b> died in a dumb way...' % m.sender.first_name, markup='HTML')

    else:
        rem_tag(m.receiver.id, 'roulette:' + str(bullets))
        bullets -= 1
        set_tag(m.receiver.id, 'roulette:' + str(bullets))
        return send_message(m, '<b>%s</b> is lucky, <b>%s</b> bullets left.' % (m.sender.first_name, bullets), markup='HTML')
