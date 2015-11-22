# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *

tags = load_json('data/tags.json')
	
def get_tags(tags, size):
    i = 4
    commands = [None] * (int(size) + 4)
    commands[0] = '^newtag'
    commands[1] = '^remtag'
    commands[2] = '^lstag'
    commands[3] = '^content'
    for tag, data in tags.items():
        commands[i] = '#' + tag
        i = i + 1
    return commands

commands = get_tags(tags, len(tags))
parameters = {
    ('name', True),
    ('type', True)
}
description = 'Use this and I will kill you.'
hidden = True

def run(msg):
    if (get_command(msg['text']) == 'newtag'
       or get_command(msg['text']) == 'content'):
        
        if get_command(msg['text']) == 'newtag':
            print 'first step'
            input = get_input(msg['text'])
            if not input:
                doc = get_doc(commands, parameters, description)
                return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

            name = first_word(input)
            type = first_word(input, 2)
            # Check if tag exists
            if name in tags:
                message = 'The tag *#' + name + '* exists!'
                if msg['from']['id'] == tags[name]['creator']:
                    message += '\nBut you can delete it with `#remtag ' + name + '`.'
                else:
                    message += '\nBut you are not allowed to delete it.'
                return send_message(msg['chat']['id'], message, parse_mode="Markdown")
            
            message = 'Reply with *' + type + '* for *#' + name + '*'
            
            force_reply_json = {'force_reply': True, 'selective': True}
            force_reply = json.dumps(force_reply_json)
            
            send_message(msg['chat']['id'], message,
                         reply_to_message_id=msg['message_id'],
                         reply_markup=force_reply,
                         parse_mode="Markdown")
        elif get_command(msg['text']) == 'content':
            print 'second step'
            name = first_word(msg['reply_to_message']['text'], 5).replace('#','')
            type = first_word(msg['reply_to_message']['text'], 3)
            
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
            if msg['from']['id'] == tags[name]['creator']:
                del tags[name]
                save_json('data/tags.json', tags)
                message = '\nYou removed the tag *#' + name + '*.'
            else:
                return send_error(msg, 'permission')
        else:
            message = 'The tag *' + name + '* is not set.'
        send_message(msg['chat']['id'], message, parse_mode="Markdown")
    elif get_command(msg['text']) == 'lstag':
        message = '*All tags*:'
        for tag, data in tags.items():
            message += '\n\t#' + str(tag) + ' | ' + data['type'] + ' | ' + str(data['creator'])
        send_message(msg['chat']['id'], message, parse_mode="Markdown")
    else:
        for tag, data in tags.items():
            if '#' + tag in msg['text']:
                if data['type'] == 'text':
                    send_message(msg['chat']['id'], data['content'], parse_mode="Markdown")
                elif data['type'] == 'audio':
                    send_audio(msg['chat']['id'], data['content'])
                elif data['type'] == 'document':
                    send_document(msg['chat']['id'], data['content'])
                elif data['type'] == 'photo':
                    send_photo(msg['chat']['id'], data['content'])
                elif data['type'] == 'sticker':
                    send_sticker(msg['chat']['id'], data['content'])
                elif data['type'] == 'video':
                    send_video(msg['chat']['id'], data['content'])
                elif data['type'] == 'voice':
                    send_voice(msg['chat']['id'], data['content'])
