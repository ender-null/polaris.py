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
    input = get_input(m)

    if get_command(m) == 'groups':
        message = lang.errors.unsupported

    elif get_command(m) == 'join':
        message = lang.errors.unsupported

    elif get_command(m) == 'invite' and (is_admin(m.sender.id) or is_mod(m.sender.id, m.receiver.id)):
        if m.reply:
            return invite_user(m, m.reply.sender.id)
        elif input:
            return invite_user(m, input)

    elif get_command(m) == 'kill' and (is_admin(m.sender.id) or is_mod(m.sender.id, m.receiver.id)):
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
        set_tag(m.sender.id, 'mod:%s' % m.receiver.id)
        message = '%s has been promoted to moderator for chat %s.' % (m.sender.first_name, m.receiver.title)

    elif get_command(m) == 'demod':
        rem_tag(m.sender.id, 'mod:%s' % m.receiver.id)
        message = '%s has been demoted to member for chat %s.' % (m.sender.first_name, m.receiver.title)

    else:
        message = lang.errors.permission

    send_message(m, message)
