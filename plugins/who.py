from core.utils import *

commands = [
    ('/who', [])
]
description = 'Gets user data.'


def run(m):
    if m.reply:
        m.receiver = m.reply.receiver
        m.sender = m.reply.sender

    if m.sender.last_name:
        message = 'Info of {0} {1}:'.format(escape_markdown(m.sender.first_name), escape_markdown(m.sender.last_name))
    else:
        message = 'Info of {0}:'.format(escape_markdown(m.sender.first_name))

    if m.sender.username:
        message += '\n👤 @{1} ({0})'.format(m.sender.id, m.sender.username)
    else:
        message += '\n👤 ({0})'.format(m.sender.id)

    if m.receiver.id < 0:
        message += '\n👥 {0} ({1})'.format(m.receiver.title, m.receiver.id)

    send_message(m, message)
