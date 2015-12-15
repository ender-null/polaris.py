# -*- coding: utf-8 -*-
from utils import *


commands = ['^who', '^fileid', '^msgid']

description = 'Gets user info.'
action = 'typing'


def run(msg):
    if 'reply_to_message' in msg:
        msg['message_id'] = msg['reply_to_message']['message_id']
        msg['from'] = msg['reply_to_message']['from']
        msg['chat'] = msg['reply_to_message']['chat']

        if 'audio' in msg['reply_to_message']:
            msg['audio'] = msg['reply_to_message']['audio']
        if 'document' in msg['reply_to_message']:
            msg['document'] = msg['reply_to_message']['document']
        if 'photo' in msg['reply_to_message']:
            msg['photo'] = msg['reply_to_message']['photo']
        if 'sticker' in msg['reply_to_message']:
            msg['sticker'] = msg['reply_to_message']['sticker']
        if 'video' in msg['reply_to_message']:
            msg['video'] = msg['reply_to_message']['video']
        if 'voice' in msg['reply_to_message']:
            msg['voice'] = msg['reply_to_message']['voice']

    if get_command(msg['text']) == 'who':
        message = '#GREETING!\n'
        if msg['from']['id'] != bot['id']:
            message += 'You\'re *' + escape_markup(msg['from']['first_name']) + '*! '
        message += 'I\'m *#BOT_FIRSTNAME*.\n'
        message += 'Nice to meet you.\n\n'
        if 'username' in msg['from']:
            message += '👤 @{0} ({1})\n'.format(escape_markup(msg['from']['username']), str(msg['from']['id']))
        else:
            message += '👤 {0}\n'.format(str(msg['from']['id']))
        if msg['chat']['type'] != 'private':
            message += '👥 {0} ({1})'.format(msg['chat']['title'], str(msg['chat']['id']))
    elif get_command(msg['text']) == 'fileid':
        message = '#GREETING!\n'
        if 'audio' in msg:
            file_id = msg['audio']['file_id']
        elif 'document' in msg:
            file_id = msg['document']['file_id']
        elif 'photo' in msg:
            file_id = msg['photo'][-1]['file_id']
        elif 'sticker' in msg:
            file_id = msg['sticker']['file_id']
        elif 'video' in msg:
            file_id = msg['video']['file_id']
        elif 'voice' in msg:
            file_id = msg['voice']['file_id']
        else:
            file_id = None

        if file_id:
            message += 'The _file id_ is:\n *' + file_id + '*'
        else:
            message += 'I couldn\'t get the file id.'
    elif get_command(msg['text']) == 'msgid':
        message = '#GREETING!\n'
        message += '*Text*: ' + str(msg['reply_to_message']['text']) + '\n'
        message += '*Message ID*: ' + str(msg['message_id']) + '\n'
        message += '*Chat ID*: ' + str(msg['chat']['id']) + '\n'

    message = tag_replace(message)

    send_message(msg['chat']['id'], message, parse_mode="Markdown")
