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
    if m.reply:
        id = m.reply.sender.id
    else:
        id = m.sender.id
    gid = m.receiver.id

    if get_command(m) == 'groups':
        message = lang.errors.unsupported

    elif get_command(m) == 'join':
        message = lang.errors.unsupported

    elif get_command(m) == 'invite' and (is_admin(id) or is_mod(id, gid)):
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)

        if m.reply:
            return invite_user(m, id)
        elif input:
            return invite_user(m, input)

    elif get_command(m) == 'kill' and (is_admin(id) or is_mod(id, gid)):
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)

        if m.reply:
            return kick_user(m, id)
        elif input:
            return kick_user(m, input)
        else:
            return kick_user(m, id)

    elif get_command(m) == 'ban':
        message = lang.errors.unsupported

    elif get_command(m) == 'addgroup':
        message = lang.errors.unsupported

    elif get_command(m) == 'remgroup':
        message = lang.errors.unsupported

    elif get_command(m) == 'addmod':
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)

        set_tag(id, 'mod:%s' % gid[1:])
        if m.reply:
            name = m.reply.sender.first_name
        else:
            name = m.sender.first_name
        message = '%s has been promoted to moderator for chat %s.' % (name, m.receiver.title)

    elif get_command(m) == 'demod':
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)

        rem_tag(id, 'mod:%s' % gid[1:])
        if m.reply:
            name = m.reply.sender.first_name
        else:
            name = m.sender.first_name

        message = '%s has been demoted to member for chat %s.' % (name, m.receiver.title)

    else:
        message = lang.errors.permission

    send_message(m, message)
