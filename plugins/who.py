from core.utils import *

commands = [
    ('/who', [])
]
description = 'Gets user data.'


def run(m):
    if m.reply:
        m.receiver = m.reply.receiver
        m.sender = m.reply.sender
    uid = str(m.sender.id)

    if m.sender.last_name:
        message = 'Info of %s %s:' % (escape_markdown(m.sender.first_name), escape_markdown(m.sender.last_name))
    else:
        message = 'Info of %s:' % (escape_markdown(m.sender.first_name))

    if m.sender.username:
        message += '\n👤 @%s (%s)' % (m.sender.username, m.sender.id)
    else:
        message += '\n👤 (%s)' % (m.sender.id)

    if m.receiver.id < 0:
        message += '\n👥 %s (%s)' % (m.receiver.title, m.receiver.id)

    if uid in tags.list:
        message += '\n🏷 %s' % (tags.list[uid])

    send_message(m, message)
