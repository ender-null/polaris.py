# -*- coding: utf-8 -*-
from utils import *
import random
import bindings_cli as cli

admincommands = [
    '^add',
    '^remove',
    '^broadcast'
]
modcommands = [
    '^modlist',
    '^modhelp',
    '^gc',
    '^promote',
    '^demote',
    '^invite',
    '^kill',
    '^suicide',
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
                message += u'\n\t-\t' + group['title']
                if group['alias'] != '':
                    message += u'\t`|{0}|`'.format(group['alias'])
                if group['realm'] != '':
                    message += u'\t`{0}`'.format(group['realm'])
    # Allows joining groups.
    elif get_command(msg['text']) == 'join':
        for gid, group in groups.items():
            if (group['alias'].lower() == input.lower() or
                group['title'].lower() == input.lower() or
                gid == input):
                if group['link'] != '':
                    message = u'*{0}*'.format(group['title'])
                    if group['alias'] != '':
                        message += u'\t|{0}|'.format(group['alias'])
                    if group['realm'] != '':
                        message += u'\t{0}'.format(group['realm'])
                    message += u'\n_{0}_\n\n[Join Group]({1})'.format(group['description'], group['link'])
                    break
                else:
                    # If no chat link is provided, adds the user.
                    cli.chat_add_user(gid, uid)
            else:
                message = 'Group not found.'
    # Shows info about the current group.
    elif get_command(msg['text']) == 'info':
        if str(cid) in groups:
            message = u'*Info of {0}*'.format(groups[str(cid)]['title'])
            if groups[str(cid)]['alias'] != '':
                message += u'\t|{0}|'.format(groups[str(cid)]['alias'])
            if groups[str(cid)]['realm'] != '':
                message += u'\t{0}'.format(groups[str(cid)]['realm'])
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
                user_id = int(input)
            else:
                user_id = int(cli.user_id(input[1:]))

            if not user_id:
                return send_error(msg, 'argument')
            return cli.chat_add_user(cid, user_id)
        elif 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
            return cli.chat_add_user(cid, user_id)
        else:
            return send_error(msg, 'id')

    elif get_command(msg['text']) == 'gc' and is_mod(msg):
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
        for uid in groups[str(cid)]['mods']:
            uid = str(uid)
            if 'alias' in users[uid]:
                message += '\n\t' + escape_markup(users[uid]['alias'])
            elif 'username' in users[uid]:
                message += '\n\t@' + escape_markup(users[uid]['username'])
            else:
                message += '\n\t`' + uid + '`'

    elif is_mod(msg) and get_command(msg['text']) == 'modhelp':
        message = '*Mod commands:*'
        for t in commands:
            t = tag_replace(t, msg)
            message += '\n\t' + t.replace('^', config['command_start'])

    elif is_mod(msg) and get_command(msg['text']) == 'broadcast':
        message = 'Unsupported action.'

    elif is_mod(msg) and (get_command(msg['text']) == 'kill'):
        i = random.randint(1, len(locale[get_locale(msg['chat']['id'])]['lastwords']))-1
        message = '`' + locale[get_locale(msg['chat']['id'])]['lastwords'][i] + '`'
        message = tag_replace(message, msg)
        
        if 'reply_to_message' in msg:
            user_id = msg['reply_to_message']['from']['id']
            send_message(cid, message, parse_mode="Markdown")
            return cli.chat_del_user(cid, user_id)

        elif input:
            if input.isdigit():
                user_id = int(input)
                name = input
                print('is digit')
            else:
                user_id = int(cli.user_id(input[1:]))
                name = input
                print('is not digit')

            if not user_id:
                return send_error(msg, 'argument')

            send_message(cid, message, parse_mode="Markdown")
            return cli.chat_del_user(cid, user_id)
            
        else:
            return send_error(msg, 'id')

    elif get_command(msg['text']) == 'suicide':
        i = random.randint(1, len(locale[get_locale(msg['chat']['id'])]['lastwords']))-1
        message = '`' + locale[get_locale(msg['chat']['id'])]['lastwords'][i] + '`'
        message = tag_replace(message, msg)
        
        user_id = msg['from']['id']
        send_message(cid, message, parse_mode="Markdown")
        return cli.chat_del_user(cid, user_id)

    elif is_mod(msg) and get_command(msg['text']) == 'promote':
        if 'reply_to_message' in msg:
            if msg['reply_to_message']['from']['id'] in groups[str(cid)]['mods']:
                message = msg['reply_to_message']['from']['first_name'] + ' is already a mod.'
                return send_message(cid, message)
            groups[str(cid)]['mods'].append(msg['reply_to_message']['from']['id'])
            message = msg['reply_to_message']['from']['first_name'] + ' is now a moderator.'
            save_json('data/groups.json', groups)
        else:
            if msg['from']['id'] in groups[str(cid)]['mods']:
                message = msg['from']['first_name'] + ' is already a mod.'
                return send_message(cid, message)
            groups[str(cid)]['mods'].append(msg['from']['id'])
            message = msg['from']['first_name'] + ' is now a moderator.'
            save_json('data/groups.json', groups)

    elif is_mod(msg) and get_command(msg['text']) == 'demote':
        if 'reply_to_message' in msg:
            if not msg['reply_to_message']['from']['id'] in groups[str(cid)]['mods']:
                message = msg['reply_to_message']['from']['first_name'] + ' is not a mod.'
                return send_message(cid, message)
            groups[str(cid)]['mods'].remove(msg['reply_to_message']['from']['id'])
            message = msg['reply_to_message']['from']['first_name'] + ' is not a moderator.'
            save_json('data/groups.json', groups)
        else:
            if not msg['from']['id'] in groups[str(cid)]['mods']:
                message = msg['from']['first_name'] + ' is not a mod.'
                return send_message(cid, message)
            groups[str(cid)]['mods'].remove(msg['from']['id'])
            message = msg['from']['first_name'] + ' is not a moderator.'
            save_json('data/groups.json', groups)

    elif get_command(msg['text']) == 'add' and is_mod(msg):
        if msg['chat']['id'] < 0:
            if groups[str(cid)]['hide'] == True:
                groups[str(cid)]['hide'] = False
                save_json('data/groups.json', groups)
                message = 'Group added.'
            else:
                message = 'Already added.'
        else:
            message = 'You can only add chat groups.'

    elif get_command(msg['text']) == 'remove' and is_mod(msg):
        if msg['chat']['id'] < 0:
            if groups[str(cid)]['hide'] == False:
                groups[str(cid)]['hide'] = True
                save_json('data/groups.json', groups)
                message = 'Group removed.'
            else:
                message = 'Already added.'
        else:
            message = 'You can only add chat groups.'
    else:
        return send_message(cid, locale[get_locale(cid)]['errors']['permission'])

    send_message(cid, message, parse_mode="Markdown")


def process(msg):
    # Updates group title in the database.
    cid = str(msg['chat']['id'])
    if ('new_chat_title' in msg and
        cid in groups):
        if (len(first_word(msg['chat']['title'])) == 1 and
            not first_word(msg['chat']['title'][0]).isalnum()):
            realm = first_word(msg['new_chat_title'])
            title = all_but_first_word(msg['new_chat_title'])
        else:
            realm = ''
            title = msg['new_chat_title']

        groups[cid]['realm'] = realm
        groups[cid]['title'] = title
        save_json('data/groups.json', groups)
    
    # Adds automaticaly groups to database.
    if not cid in groups and int(cid) < 0:
        if (len(first_word(msg['chat']['title'])) == 1 and
            not first_word(msg['chat']['title'][0]).isalnum()):
            realm = first_word(msg['chat']['title'])
            title = all_but_first_word(msg['chat']['title'])
        else:
            realm = ''
            title = msg['chat']['title']

        groups[cid] = OrderedDict()
        groups[cid]['title'] = title
        groups[cid]['description'] = 'Group automaticaly added.'
        groups[cid]['realm'] = realm
        groups[cid]['rules'] = ''
        groups[cid]['mods'] = [msg['from']['id']]
        groups[cid]['link'] = ''
        groups[cid]['alias'] = ''
        groups[cid]['locale'] = 'default'
        groups[cid]['hide'] = True
        groups[cid]['special'] = None

        save_json('data/groups.json', groups)

def cron():
    groups = load_json('data/groups.json', True)
