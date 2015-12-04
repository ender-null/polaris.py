# -*- coding: utf-8 -*-
from utilies import *
import bindings_cli as cli

admincommands = [
    '^add',
    '^remove',
    '^broadcast'
]
modcommands = [
    '^modlist',
    '^modhelp',
    '^groupconfig',
    '^promote',
    '^demote',
    '^invite',
    '^kill',
    '^exterminate'
]
commands = [
    '^groups',
    '^join',
    '^info',
    '^rules'
]
commands.extend(modcommands)
commands.extend(admincommands)

description = 'Allows basic group management features, like joining groups. Some features needs @PolarisBotB to be in the group as an Admin.'
action = 'typing'


def run(msg):
    # Gets input and set the default message as an Argument Error.
    input = get_input(msg['text'])
    cid = msg['chat']['id']
    uid = msg['from']['id']
    message = loc(cid)['errors']['argument']


    # Shows a list of public groups.
    if get_command(msg['text']) == 'groups':
        message = '*Groups:*'
        for gid, group in groups.items():
            if not group['hide']:
                message += '\n\t'
                if group['link'] != '':
                    message += u'[{0}]({1})'.format(group['title'], group['link'])
                else:
                    message += group['title']
                message += u'\t{0}'.format(group['realm'])
                if 'alias' in group:
                    message += u'\t({0})'.format(group['alias'])

    elif get_command(msg['text']) == 'join':
        print get_command(msg['text'])
        for gid, group in groups.items():
            if group['alias'].lower() == input.lower():
                if group['link'] != '':
                    message = u'*{0}*'.format(group['title'])
                    if group['alias']:
                        message += u'\t_[{0}]_'.format(group['alias'])
                    message += u'\n_{0}_\n\n[Join Group]({1})'.format(group['description'], group['link'])
                    break
                else:
                    # If no chat link is provided, adds the user.
                    cli.chat_add_user(gid, uid)
            else:
                message = 'Group not found.'

    elif get_command(msg['text']) == 'info':
        if str(cid) in groups:
            message = u'*Info of {0}*'.format(groups[str(cid)]['title'])
            if groups[str(cid)]['alias'] != '':
                message += u'\t_[{0}]_'.format(groups[str(cid)]['alias'])
            message += u'\n{0}'.format(groups[str(cid)]['description'])
            if groups[str(cid)]['rules'] != '':
                message += u'\n\n*Rules:*\n{0}'.format(groups[str(cid)]['rules'])
            if groups[str(cid)]['locale'] != 'default':
                message += '\n\n*Locale:* _{0}_'.format(groups[str(cid)]['locale'])
            if groups[str(cid)]['link'] != '':
                message += '\n\n*Invite link:*\n{0}'.format(get_short_url(groups[str(cid)]['link']))

        else:
            message = 'Group not added.'


    elif get_command(msg['text']) == 'rules':
        if str(cid) in groups:
            if groups[str(cid)]['rules'] != '':
                message = u'*Rules:*\n' + groups[str(cid)]['rules']
            else:
                message = '_No rules_'
        else:
            message = 'Group not added.'

    elif get_command(msg['text']) == 'invite' and is_mod(msg):
        if input:
            if input.isdigit():
                user_id = input
                name = input
            else:
                user_id = cli.user_id(input[1:])
                name = input

            if not user_id:
                return send_error(msg, 'argument')

            message = 'Adding *' + name + '* to *' + msg['chat']['title'] + '*.'
            send_message(cid, message, parse_mode="Markdown")
            cli.chat_add_user(cid, user_id)

            for gid, group in groups.items():
                if group['special'] == 'admin':
                    message = 'Added *' + name + '* to *' + msg['chat']['title'] + '* by ' + msg['from']['first_name']
                    send_message(gid, message, parse_mode="Markdown")
            return
        elif 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
            name = '@' + msg['reply_to_message']['from']['username']
            message = 'Adding *' + name + '* to *' + msg['chat']['title'] + '*.'
            send_message(cid, message, parse_mode="Markdown")
            cli.chat_add_user(cid, user_id)
        else:
            return send_error(msg, 'id')

    elif get_command(msg['text']) == 'groupconfig' and is_mod(msg):
        if first_word(input) == 'link':
            groups[str(cid)]['link'] = all_but_first_word(input)
            message = 'Updated invite link of ' + groups[str(cid)]['title'] + '.'

        elif first_word(input) == 'alias':
            groups[str(cid)]['alias'] = all_but_first_word(input)
            message = 'Updated alias of ' + groups[str(cid)]['title'] + '.'

        elif first_word(input) == 'realm':
            groups[str(cid)]['realm'] = all_but_first_word(input)
            message = 'Updated realm of ' + groups[str(cid)]['title'] + '.'

        elif first_word(input) == 'description':
            groups[str(cid)]['description'] = all_but_first_word(input)
            message = 'Updated description of ' + groups[str(cid)]['title'] + '.'

        elif first_word(input) == 'rules':
            groups[str(cid)]['rules'] = all_but_first_word(input)
            message = 'Updated rules of ' + groups[str(cid)]['title'] + '.'

        elif first_word(input) == 'locale':
            groups[str(cid)]['locale'] = all_but_first_word(input)
            message = 'Updated locale of ' + groups[str(cid)]['title'] + '.'

        elif first_word(input) == 'hide':
            if all_but_first_word(input) == 'true':
                groups[str(cid)]['hide'] = true
            else:
                groups[str(cid)]['hide'] = false

            message = 'Updated hide status of ' + groups[str(cid)]['title'] + '.'

        save_json('data/groups.json', groups)

    elif get_command(msg['text']) == 'modlist':
        message = '*Mods for ' + groups[str(cid)]['title'] + ':*'
        for mod in groups[str(cid)]['mods'].items():
            message += '\n\t' + mod[1]

    elif is_mod(msg) and get_command(msg['text']) == 'modhelp':
        message = '*Mod commands:*'
        for t in commands:
            t = tag_replace(t, msg)
            message += '\n\t' + t.replace('^', config['command_start'])

    elif is_mod(msg) and get_command(msg['text']) == 'broadcast':
        message = 'Unsupported action.'

    elif is_mod(msg) and (get_command(msg['text']) == 'kill' or get_command(msg['text']) == 'exterminate'):
        if 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
            name = '@' + msg['reply_to_message']['from']['username']

            message = '`EX-TER-MIN-ATE!`'
            send_message(cid, message, parse_mode="Markdown")
            cli.chat_del_user(cid, user_id)
        elif input:
            if input.isdigit():
                user_id = input
                name = input
            else:
                user_id = cli.user_id(input[1:])
                name = input

            if not user_id:
                return send_error(msg, 'argument')

            message = '`EX-TER-MIN-ATE!`'
            send_message(cid, message, parse_mode="Markdown")
            cli.chat_del_user(cid, user_id)

            for group in groups.items():
                if group[1]['special'] == 'admin':
                    message = 'Kicked *' + name + '* from *' + msg['chat']['title'] + '* by ' + msg['from'][
                        'first_name']
                    send_message(group[0], message, parse_mode="Markdown")
            return
        else:
            return send_error(msg, 'id')

    elif is_mod(msg) and get_command(msg['text']) == 'promote':
        if 'reply_to_message' in msg:
            groups[str(cid)]['mods'][str(msg['reply_to_message']['from']['id'])] = str(
                msg['reply_to_message']['from']['first_name'])
            message = msg['reply_to_message']['from']['first_name'] + ' is now a moderator.'
            save_json('data/groups.json', groups)
        else:
            return send_message(cid, locale[get_locale(cid)]['errors']['id'])

    elif is_mod(msg) and get_command(msg['text']) == 'demote':
        if 'reply_to_message' in msg:
            del groups[str(cid)]['mods'][str(msg['reply_to_message']['from']['id'])]
            message = msg['reply_to_message']['from']['first_name'] + ' is not a moderator.'
            save_json('data/groups.json', groups)
        else:
            return send_message(cid, locale[get_locale(cid)]['errors']['id'])

    elif get_command(msg['text']) == 'add' and is_mod(msg):
        if msg['chat']['type'] == 'group':
            if not str(cid) in groups:
                if len(first_word(msg['chat']['title'])) == 1:
                    realm = first_word(msg['chat']['title'])
                    title = all_but_first_word(msg['chat']['title'])
                else:
                    realm = ''
                    title = msg['chat']['title']

                groups[str(cid)] = OrderedDict()
                groups[str(cid)]['link'] = ''
                groups[str(cid)]['realm'] = realm
                groups[str(cid)]['title'] = title
                groups[str(cid)]['description'] = 'Group added by ' + msg['from']['first_name']
                groups[str(cid)]['rules'] = ''
                groups[str(cid)]['locale'] = 'default'
                groups[str(cid)]['special'] = None
                groups[str(cid)]['alias'] = ''
                groups[str(cid)]['hide'] = False
                groups[str(cid)]['mods'] = {}
                groups[str(cid)]['mods'][msg['from']['id']] = msg['from']['first_name']
                groups[str(cid)]['mods'] = {}

                save_json('data/groups.json', groups)

                message = 'Group added.'
            else:
                message = 'Already added.'
        else:
            message = 'You can only add chat groups.'

    elif get_command(msg['text']) == 'remove' and is_mod(msg):
        del groups[str(cid)]
        message = 'Group removed.'
    else:
        return send_message(cid, locale[get_locale(cid)]['errors']['permission'])

    send_message(cid, message, parse_mode="Markdown")


def process(msg):
    # Updates group title in the database.
    cid = msg['chat']['id']
    if ('new_chat_title' in msg and
        cid in groups):
        if len(first_word(msg['new_chat_title'])) == 1:
            realm = first_word(msg['new_chat_title'])
            title = all_but_first_word(msg['new_chat_title'])
        else:
            realm = ''
            title = msg['new_chat_title']

        groups[str(cid)]['realm'] = realm
        groups[str(cid)]['title'] = title
        save_json('data/groups.json', groups)


def cron():
    groups = load_json('data/groups.json', True)
