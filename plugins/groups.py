from core.utils import *

commands = [
    ('/groups', []),
    ('/join', ['alias | chat id', '']),
    ('/invite', ['username | user id']),
    ('/kill', ['username | user id']),
    ('/ban', ['username | user id']),
    ('/addgroup', []),
    ('/remgroup', [])
]

def run(m):
    if not is_admin(m.sender.id):
        send_message(m, m.sender.first_name + ' tried to use and admin command. ')
        return send_message(m, 'No, shit isn\'t going that way.')

    input = get_input(m)

    if get_command(m) == 'groups':
        message = 'Unsupported action!'

    elif get_command(m) == 'join':
        message = 'Unsupported action!'

    elif get_command(m) == 'invite':
        if m.reply:
            send_message(m, 'Inviting user ' + m.reply.sender.id)
            return invite_user(m, m.reply.sender.id)
        message = 'Unsupported action!'

    elif get_command(m) == 'kill':
        if m.reply:
            send_message(m, 'Killing user ' + m.reply.sender.id)
            return kick_user(m, m.reply.sender.id)
        message = 'Unsupported action!'

    elif get_command(m) == 'ban':
        message = 'Unsupported action!'

    elif get_command(m) == 'addgroup':
        message = 'Unsupported action!'

    elif get_command(m) == 'remgroup':
        message = 'Unsupported action!'

    send_message(m, message)