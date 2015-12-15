# -*- coding: utf-8 -*-
from utils import *

tags = load_json('data/tags.json')
def get_tags(tags):
    i = 4
    commands = [None] * (len(tags) + i)
    commands[0] = '^taglist'
    commands[1] = '^newtag'
    commands[2] = '^remtag'
    commands[3] = '^content'
    for tag, data in tags.items():
        commands[i] = '#' + tag
        i = i + 1
    return commands


commands = get_tags(tags)
parameters = {
    ('name', True),
    ('type', True)
}
description = 'Use this and I will kill you.'
hidden = True


def run(msg):
    types = [
        'text',
        'photo',
        'document',
        'voice',
        'audio',
        'sticker',
        'video',
        'alias'
    ]
    if (get_command(msg['text']) == 'newtag'
        or get_command(msg['text']) == 'content'):

        if get_command(msg['text']) == 'newtag':
            input = get_input(msg['text'])
            if not input:
                doc = get_doc(commands, parameters, description)
                return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

            name = first_word(input)
            type = first_word(input, 2)
            
            # Check if it's a reply and extract media from it
            if 'reply_to_message' in msg:
                if 'audio' in msg['reply_to_message']:
                    type = 'audio'
                    content = msg['reply_to_message']['audio']['file_id']
                elif 'document' in msg['reply_to_message']:
                    type = 'document'
                    content = msg['reply_to_message']['document']['file_id']
                elif 'photo' in msg['reply_to_message']:
                    type = 'photo'
                    content = msg['reply_to_message']['photo'][-1]['file_id']
                elif 'sticker' in msg['reply_to_message']:
                    type = 'sticker'
                    content = msg['reply_to_message']['sticker']['file_id']
                elif 'video' in msg['reply_to_message']:
                    type = 'video'
                    content = msg['reply_to_message']['video']['file_id']
                elif 'voice' in msg['reply_to_message']:
                    type = 'voice'
                    content = msg['reply_to_message']['voice']['file_id']
                elif 'text' in msg['reply_to_message']:
                    type = 'text'
                    content = msg['reply_to_message']['text'].replace(first_word(msg['reply_to_message']['text']) + ' ', '')
                else:
                    content = None
            else:
                content = None

            # Check if tag exists
            if name in tags:
                message = 'The tag *#' + name + '* exists!'
                if msg['from']['id'] == tags[name]['creator']:
                    message += '\nBut you can delete it with `' + config['command_start'] + 'remtag ' + name + '`.'
                else:
                    message += '\nBut you are not allowed to delete it.'
                return send_message(msg['chat']['id'], message, parse_mode="Markdown")
            if not type:
                return send_error(msg, 'argument')
            if not type in types:
                message = 'You need to provide a valid type.'
                return send_message(msg['chat']['id'], message, parse_mode="Markdown")
            if content:
                tag = OrderedDict()
                tag['creator'] = msg['from']['id']
                tag['type'] = type
                tag['content'] = content
                tags[name] = tag
                save_json('data/tags.json', tags)

                message = 'Added tag *#' + name + '* for that *' + type + '*.'
                return send_message(msg['chat']['id'], message,
                             reply_to_message_id=msg['message_id'],
                             parse_mode="Markdown")

            message = 'Reply with a *' + type + '* for the tag *#' + name + '*'

            force_reply_json = {'force_reply': True, 'selective': True}
            force_reply = json.dumps(force_reply_json)

            send_message(msg['chat']['id'], message,
                         reply_to_message_id=msg['message_id'],
                         reply_markup=force_reply,
                         parse_mode="Markdown")
        elif get_command(msg['text']) == 'content':
            name = first_word(msg['reply_to_message']['text'], 8).replace('#', '')
            type = first_word(msg['reply_to_message']['text'], 4)

            tag = OrderedDict()
            tag['creator'] = msg['from']['id']
            tag['type'] = type
            if type == 'text':
                tag['content'] = msg['text'].replace(first_word(msg['text']) + ' ', '')
            elif type == 'audio':
                tag['content'] = msg['audio']['file_id']
            elif type == 'document':
                tag['content'] = msg['document']['file_id']
            elif type == 'photo':
                tag['content'] = msg['photo'][-1]['file_id']
            elif type == 'sticker':
                tag['content'] = msg['sticker']['file_id']
            elif type == 'video':
                tag['content'] = msg['video']['file_id']
            elif type == 'voice':
                tag['content'] = msg['voice']['file_id']

            tags[name] = tag
            save_json('data/tags.json', tags)

            message = 'Added tag *#' + name + '* for that *' + type + '*.'
            send_message(msg['chat']['id'], message,
                         reply_to_message_id=msg['message_id'],
                         parse_mode="Markdown")
    elif get_command(msg['text']) == 'remtag':
        input = get_input(msg['text'])
        if not input:
            doc = get_doc(commands, parameters, description)
            return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

        name = first_word(input)
        if name in tags:
            if msg['from']['id'] == tags[name]['creator'] or is_admin(msg):
                del tags[name]
                save_json('data/tags.json', tags)
                message = '\nYou removed the tag *#' + name + '*.'
            else:
                return send_error(msg, 'permission')
        else:
            message = 'The tag *' + name + '* is not set.'
        send_message(msg['chat']['id'], message, parse_mode="Markdown")
    elif get_command(msg['text']) == 'taglist':
        #taglist = [None] * len(tags)
        #i = 0
        #for tag, data in tags.items():
        #    taglist[i] = '\n\t#' + str(tag) + ' | ' + data['type'] + ' | ' + str(data['creator'])
        #    i += 1
        #i = 0
        #while i <= len(taglist):
        #    message = ''
        #    while i < 40:
        #        message += taglist[i]
        #    send_message(msg['chat']['id'], message, parse_mode="Markdown")
        #    i += 40
        message = '`#GiTGuD`'
        send_message(msg['chat']['id'], message, parse_mode="Markdown")
    else:
        for tag, data in tags.items():
            if '#' + tag.lower() in msg['text'].lower():
                if data['type'] == 'text':
                    if 'markdown' in data and data['markdown']:
                        if not send_message(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id'], parse_mode="Markdown"):
                            send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    else:
                        if not send_message(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id']):
                            send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    break
                elif data['type'] == 'audio':
                    if not send_audio(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id']):
                        send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    break
                elif data['type'] == 'document':
                    if not send_document(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id']):
                        send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    break
                elif data['type'] == 'photo':
                    if not send_photo(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id']):
                        send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    break
                elif data['type'] == 'sticker':
                    if not send_sticker(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id']):
                        send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    break
                elif data['type'] == 'video':
                    if not send_video(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id']):
                        send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    break
                elif data['type'] == 'voice':
                    if not send_voice(msg['chat']['id'], data['content'], reply_to_message_id=msg['message_id']):
                        send_message(msg['chat']['id'], '`#lolnope`', reply_to_message_id=msg['message_id'], parse_mode="Markdown")
                    break


def process(msg):
    if ('reply_to_message' in msg and
                'text' in msg['reply_to_message'] and
                msg['reply_to_message']['from']['id'] == bot['id'] and
            msg['reply_to_message']['text'].startswith('Reply with ')):
        if 'text' in msg:
            msg['text'] = config['command_start'] + 'content ' + msg['text']
        else:
            msg['text'] = config['command_start'] + 'content'

def cron():
    tags = load_json('data/tags.json', True)