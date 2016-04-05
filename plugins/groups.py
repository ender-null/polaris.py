from core.utils import *

commands = [
    ('/groups', []),
    ('/join', ['alias | chat id']),
    ('/mods', []),
    ('/info', []),
    ('/suicide', []),
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
    uid = m.sender.id
    gid = m.receiver.id

    if get_command(m) == 'groups':
        message = lang.errors.unsupported

    elif get_command(m) == 'join':
        message = lang.errors.unsupported
    
    elif get_command(m) == 'mods':
        message = ''
        mods = ''
        globalmods = ''
        admins = ''
        
        for uid in tags.list:
            if 'mod:' + str(m.receiver.id)[1:] in tags.list[uid]:
                mods += '\t%s\n' % user_info(int(uid))
            if 'globalmod' in tags.list[uid]:
                globalmods += '\t%s\n' % user_info(int(uid))
            if 'admin' in tags.list[uid]:
                admins += '\t%s\n' % user_info(int(uid))
        if len(mods) > 0:
            message += 'Group mods: \n%s\n' % mods
        if len(globalmods) > 0:
            message += 'Globalmods: \n%s\n' % globalmods
        if len(admins) > 0:
            message += 'Admins: \n%s\n' % admins
        
    elif get_command(m) == 'suicide':
        message = lang.errors.unsupported
	
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)
            
        res = kick_user(m, uid)
        if res is None:
            return send_message(m, lang.errors.notchatadmin)
        elif not res:
            return send_message(m, lang.errors.failed)
        else:
            return send_message(m, 'Ｄｕｍｂ  ｗａｙｓ  ｔｏ  ｄｉｅ．')

    elif get_command(m) == 'invite' and (is_admin(uid) or is_mod(uid, gid)):
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)

        if m.reply:
            target = id
        elif input:
            target = input

        res = invite_user(m, target)
        if res is None:
            return send_message(m, lang.errors.peerflood)
        elif not res:
            return send_message(m, lang.errors.failed)
        else:
            return

    elif get_command(m) == 'kill' and (is_admin(uid) or is_mod(uid, gid)):
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)

        if m.reply:
            target = id
        elif input:
            target = input
        else:
            target = uid
            
        res = kick_user(m, target)
        if res is None:
            return send_message(m, lang.errors.notchatadmin)
        elif not res:
            return send_message(m, lang.errors.failed)
        else:
            return send_message(m, 'Ａｎ  ｅｎｅｍｙ  ｈａｓ  ｂｅｅｎ  ｓｌａｉｎ．')

    elif get_command(m) == 'ban':
        message = lang.errors.unsupported

    elif get_command(m) == 'addgroup':
        message = lang.errors.unsupported

    elif get_command(m) == 'remgroup':
        message = lang.errors.unsupported

    elif get_command(m) == 'addmod' and (is_admin(uid) or is_mod(uid, str(gid)[1:])):
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)
            
        if m.reply:
            name = m.reply.sender.first_name
        else:
            name = m.sender.first_name
                
        if not has_tag(id, 'mod:%s' % str(gid)[1:]):
            set_tag(id, 'mod:%s' % str(gid)[1:])
            message = '%s has been promoted to moderator for chat %s.' % (name, m.receiver.title)
        else:
            message = '%s is already a moderator for chat %s.' % (name, m.receiver.title)

    elif get_command(m) == 'demod' and (is_admin(uid) or is_mod(uid, str(gid)[1:])):
        if m.receiver.id > 0:
            return send_message(m, lang.errors.unsupported)
            
        if m.reply:
            name = m.reply.sender.first_name
        else:
            name = m.sender.first_name
            
        if has_tag(id, 'mod:%s' % str(gid)[1:]):
            rem_tag(id, 'mod:%s' % str(gid)[1:])
            message = '%s has been demoted to member for chat %s.' % (name, m.receiver.title)
        else:
            message = '%s is not a moderator for %s.' % (name, m.receiver.title)

    else:
        message = lang.errors.permission

    send_message(m, message)
