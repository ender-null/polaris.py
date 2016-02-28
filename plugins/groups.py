from core.utils import *

commands = [
    ('/groups', []),
    ('/join', ['alias | chat id']),
    ('/invite', ['username | user id']),
    ('/kill', ['username | user id']),
    ('/ban', ['username | user id']),
    ('/addgroup', []),
    ('/remgroup', [])
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
        message = 'Unsupported action!'

    elif get_command(m) == 'kill':
        if m.reply:
            return kick_user(m, m.reply.sender.id)
        message = 'Unsupported action!'

    elif get_command(m) == 'ban':
        message = 'Unsupported action!'

    elif get_command(m) == 'addgroup':
        message = 'Unsupported action!'

    elif get_command(m) == 'remgroup':
        message = 'Unsupported action!'

    send_message(m, message)