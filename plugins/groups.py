# -*- coding: utf-8 -*-
from utilies import *
import bindings_cli as cli

commands = [
    '^info',
    '^desc',
    '^rules',
    '^join',
    '^groups',
    '^modlist',
    '^modhelp',
    '^add',
    '^remove',
    '^set',
    '^kill',
    '^exterminate',
    '^invite',
    '^broadcast',
    '^promote',
    '^demote'
]

hidden = True

def run(msg):
    input = get_input(msg['text'])

    message = locale['default']['errors']['argument']

    if is_mod(msg) and get_command(msg['text']) == 'add':
        if msg['chat']['type'] == 'group':
            if not str(msg['chat']['id']) in groups:
                if len(first_word(msg['chat']['title'])) == 1:
                    realm = first_word(msg['chat']['title'])
                    title = all_but_first_word(msg['chat']['title'])
                else:
                    realm = ''
                    title = msg['chat']['title']

                groups[str(msg['chat']['id'])] = OrderedDict()
                groups[str(msg['chat']['id'])]['link'] = ''
                groups[str(msg['chat']['id'])]['realm'] = realm
                groups[str(msg['chat']['id'])]['title'] = title
                groups[str(msg['chat']['id'])]['description'] = 'Group added by ' + msg['from']['first_name']
                groups[str(msg['chat']['id'])]['rules'] = ''
                groups[str(msg['chat']['id'])]['locale'] = 'default'
                groups[str(msg['chat']['id'])]['special'] = None
                groups[str(msg['chat']['id'])]['alias'] = ''
                groups[str(msg['chat']['id'])]['hide'] = False
                groups[str(msg['chat']['id'])]['mods'] = {}
                groups[str(msg['chat']['id'])]['mods'][msg['from']['id']] = msg['from']['first_name']

                save_json('data/groups.json', groups)

                message = 'Group added.'
            else:
                message = 'Already added.'
        else:
            message = 'You can only add chat groups.'

    elif is_mod(msg) and get_command(msg['text']) == 'remove':
        del groups[str(msg['chat']['id'])]
        message = 'Group removed.'

    elif is_mod(msg) and get_command(msg['text']) == 'set':
        if first_word(input) == 'link':
            groups[str(msg['chat']['id'])]['link'] = all_but_first_word(input)
            message = 'Updated invite link of ' + groups[str(msg['chat']['id'])]['title'] + '.'

        elif first_word(input) == 'alias':
            groups[str(msg['chat']['id'])]['alias'] = all_but_first_word(input)
            message = 'Updated alias of ' + groups[str(msg['chat']['id'])]['title'] + '.'

        elif first_word(input) == 'realm':
            groups[str(msg['chat']['id'])]['realm'] = all_but_first_word(input)
            message = 'Updated realm of ' + groups[str(msg['chat']['id'])]['title'] + '.'

        elif first_word(input) == 'description':
            groups[str(msg['chat']['id'])]['description'] = all_but_first_word(input)
            message = 'Updated description of ' + groups[str(msg['chat']['id'])]['title'] + '.'

        elif first_word(input) == 'rules':
            groups[str(msg['chat']['id'])]['rules'] = all_but_first_word(input)
            message = 'Updated rules of ' + groups[str(msg['chat']['id'])]['title'] + '.'

        elif first_word(input) == 'locale':
            groups[str(msg['chat']['id'])]['locale'] = all_but_first_word(input)
            message = 'Updated locale of ' + groups[str(msg['chat']['id'])]['title'] + '.'

        elif first_word(input) == 'hide':
            if all_but_first_word(input) == 'true':
                groups[str(msg['chat']['id'])]['hide'] = true
            else:
                groups[str(msg['chat']['id'])]['hide'] = false

            message = 'Updated hide status of ' + groups[str(msg['chat']['id'])]['title'] + '.'

        save_json('data/groups.json', groups)

    elif get_command(msg['text']) == 'groups':
        message = '*Groups:*'
        for group in groups.items():
            if group[1]['hide'] != True:
                message += '\n\t'

                if 'link' in group[1]:
                    message += '[' + group[1]['title'] + '](' + group[1]['link'] + ')'
                else:
                    message += group[1]['title']

                message += '\t' + group[1]['realm']

                if 'alias' in group[1]:
                    message += '\t(' + group[1]['alias'] + ')'

    elif get_command(msg['text']) == 'modlist':
        message = '*Mods for ' + groups[str(msg['chat']['id'])]['title'] + ':*'
        for mod in groups[str(msg['chat']['id'])]['mods'].items():
            message += '\n\t' + mod[1]

    elif is_mod(msg) and get_command(msg['text']) == 'modhelp':
        message = '*Mod commands:*'
        for t in commands:
            t = tag_replace(t, msg)
            message += '\n\t' + t.replace('^', config['command_start'])

    elif get_command(msg['text']) == 'info':
        if str(msg['chat']['id']) in groups:
            message = '*Info of ' + groups[str(msg['chat']['id'])]['title'] + '*'
            if groups[str(msg['chat']['id'])]['alias'] != '':
                message += '\t_[' + groups[str(msg['chat']['id'])]['alias'] + ']_'
            message += '\n' + groups[str(msg['chat']['id'])]['description']
            if groups[str(msg['chat']['id'])]['rules'] != '':
                message += '\n\n*Rules:*\n' + groups[str(msg['chat']['id'])]['rules']
            if groups[str(msg['chat']['id'])]['locale'] != 'default':
                message += '\n\n*Locale:* _' + groups[str(msg['chat']['id'])]['locale'] + '_'
            if groups[str(msg['chat']['id'])]['link'] != '':
                message += '\n\n*Invite link:*\n' + groups[str(msg['chat']['id'])]['link']
        else:
            message = 'Group not added.'

    elif is_mod(msg) and get_command(msg['text']) == 'broadcast':
        message = 'Unsupported action.'

    elif is_mod(msg) and (get_command(msg['text']) == 'kill' or get_command(msg['text']) == 'exterminate'):
        if 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
            name = '@' + msg['reply_to_message']['from']['username']
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
            send_message(msg['chat']['id'], message, parse_mode="Markdown")
            cli.chat_del_user(msg['chat']['id'], user_id)
            
            for group in groups.items():
                if group[1]['special'] == 'admin':
                    message = 'Kicked *' + name + '* from *' + msg['chat']['title'] + '* by ' + msg['from']['first_name']
                    send_message(group[0], message, parse_mode="Markdown")
            return
        else:
            return send_error(msg, 'id')
    elif is_mod(msg) and get_command(msg['text']) == 'invite':
        if 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
            name = '@' + msg['reply_to_message']['from']['username']
        elif input:
            if input.isdigit():
                user_id = input
                name = input
            else:
                user_id = cli.user_id(input[1:])
                name = input

            if not user_id:
                return send_error(msg, 'argument')
            
            message = 'Adding *' + name + '* to *' + msg['chat']['title'] + '*.'
            send_message(msg['chat']['id'], message, parse_mode="Markdown")
            cli.chat_add_user(msg['chat']['id'], user_id)
            
            for group in groups.items():
                if group[1]['special'] == 'admin':
                    message = 'Added *' + name + '* to *' + msg['chat']['title'] + '* by ' + msg['from']['first_name']
                    send_message(group[0], message, parse_mode="Markdown")
            return
        else:
            return send_error(msg, 'id')

    elif get_command(msg['text']) == 'desc':
        if str(msg['chat']['id']) in groups:
            if groups[str(msg['chat']['id'])]['description'] != '':
                message = '*Description:*\n' + groups[str(msg['chat']['id'])]['description']
            else:
                message = '_No description_'
        else:
            message = 'Group not added.'

    elif get_command(msg['text']) == 'rules':
        if str(msg['chat']['id']) in groups:
            if groups[str(msg['chat']['id'])]['rules'] != '':
                message = '*Rules:*\n' + groups[str(msg['chat']['id'])]['rules']
            else:
                message = '_No rules_'
        else:
            message = 'Group not added.'

    elif is_mod(msg) and get_command(msg['text']) == 'promote':
        if 'reply_to_message' in msg:
            groups[str(msg['chat']['id'])]['mods'][str(msg['reply_to_message']['from']['id'])] = str(msg['reply_to_message']['from']['first_name'])
            message = msg['reply_to_message']['from']['first_name'] + ' is now a moderator.'
            save_json('data/groups.json', groups)
        else:
            return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['id'])

    elif is_mod(msg) and get_command(msg['text']) == 'demote':
        if 'reply_to_message' in msg:
            del groups[str(msg['chat']['id'])]['mods'][str(msg['reply_to_message']['from']['id'])]
            message = msg['reply_to_message']['from']['first_name'] + ' is not a moderator.'
            save_json('data/groups.json', groups)
        else:
            return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['id'])

    elif get_command(msg['text']) == 'join':
        for group in groups.items():
            if group[1]['alias'].lower() == input.lower():
                if group[1]['link'] != '':
                    message = '*' + group[1]['title'] + '*'
                    if group[1]['alias'] != '':
                        message += '\t_[' + group[1]['alias'] + ']_'
                    message += '\n_' + group[1]['description'] + '_'
                    '''if group[1]['rules'] != '':
                        message += '\n\n*Rules*:\n' + group[1]['rules']'''
                    message += '\n\n[Join Group](' + group[1]['link'] + ')'
                    break
                else:
                    message = 'No invite link available.'
            else:
                message = 'Group not found.'
    else:
        print 'else ' + get_command(msg['text'])
        return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['permission'])

    send_message(msg['chat']['id'], message, parse_mode="Markdown")

def cron():
    groups = load_json('data/groups.json', True)