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


def run(m):
    if not is_admin(m.sender.id):
        return send_message(m, 'No, shit isn\'t going that way.')

    input = get_input(m)

    if get_command(m) == 'groups':
        message = 'Unsupported action!'

    elif get_command(m) == 'join':
        message = 'Unsupported action!'

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
        message = 'Unsupported action!'

    elif get_command(m) == 'addgroup':
        message = 'Unsupported action!'

    elif get_command(m) == 'remgroup':
        message = 'Unsupported action!'

    elif get_command(m) == 'addmod':
        message = 'Unsupported action!'

    elif get_command(m) == 'demod':
        message = 'Unsupported action!'

    send_message(m, message)