from core.utils import *

commands = [
    ('/groups', []),
    ('/join', ['alias | chat id']),
    ('/invite', ['user']),
    ('/kill', ['user']),
    ('/ban', ['user']),
    ('/addgroup', []),
    ('/remgroup', []),
    ('/addmod', ['user']),
    ('/demod', ['user'])
]
description = 'Group management features. Currently very experimental and unstable.'
hidden = True


def run(m):
    if not is_trusted(m.sender.id):
        return send_message(m, lang.errors.permission)

    input = get_input(m)

    if get_command(m) == 'groups':
        message = lang.errors.unsupported

    elif get_command(m) == 'join':
        message = lang.errors.unsupported

    elif get_command(m) == 'invite':
        if m.reply:
            return invite_user(m, m.reply.sender.id)
        elif input:
            return invite_user(m, input)

    elif get_command(m) == 'kill':
        if m.reply:
            return kick_user(m, m.reply.sender.id)
        elif input:
            return kick_user(m, input)
        else:
            return kick_user(m, m.sender.id)

    elif get_command(m) == 'ban':
        message = lang.errors.unsupported

    elif get_command(m) == 'addgroup':
        message = lang.errors.unsupported

    elif get_command(m) == 'remgroup':
        message = lang.errors.unsupported

    elif get_command(m) == 'addmod':
        message = lang.errors.unsupported

    elif get_command(m) == 'demod':
        message = lang.errors.unsupported

    send_message(m, message)
