# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *

tags = load_json('data/tags.json')
	
def get_tags(tags, size):
    i = 2
    commands = [None] * (int(size) + 2)
    commands[0] = '^tag'
    commands[1] = '^content'
    for tag, data in tags.items():
        commands[i] = '#' + tag
        i = i + 1
    return commands

commands = get_tags(tags, len(tags))
parameters = {
    ('name', True),
    ('type', True)
}
description = 'Experiment.'
hidden = True

def run(msg):
    if (get_command(msg['text']) == 'tag'
       or get_command(msg['text']) == 'content'):
        print 'new tag'
        input = get_input(msg['text'])

        if not input:
            doc = get_doc(commands, parameters, description)
            return send_message(msg['chat']['id'], doc, parse_mode="Markdown")
        
        if get_command(msg['text']) == 'tag':
            print 'first step'
            name = first_word(input)
            type = first_word(input, 2)
            message = 'Reply with *' + type + '* for *#' + name + '*: '
            
            force_reply_json = {'force_reply': True, 'selective': True}
            force_reply = json.dumps(force_reply_json)
            
            send_message(msg['chat']['id'], message,
                         reply_to_message_id=msg['message_id'],
                         reply_markup=force_reply,
                         parse_mode="Markdown")
        elif get_command(msg['text']) == 'content':
            print 'second step'
            if not input:
                return
            tags = load_json('data/tags.json')
            
            name = first_word(msg['reply_to_message']['text'], 5).replace('#','')
            type = first_word(msg['reply_to_message']['text'], 3)
            
            tag = OrderedDict()
            tag['creator'] = msg['from']['id']
            tag['type'] = type
            if type == 'text':
                tag['content'] = msg['text'].replace(first_word(msg['text']) + ' ', '')
            elif type == 'audio':
                tag['content'] = msg['reply_to_message']['audio']['file_id']
            elif type == 'document':
                tag['content'] = msg['reply_to_message']['document']['file_id']
            elif type == 'photo':
                tag['content'] = msg['reply_to_message']['photo'][-1]['file_id']
            elif type == 'sticker':
                tag['content'] = msg['reply_to_message']['sticker']['file_id']
            elif type == 'video':
                tag['content'] = msg['reply_to_message']['video']['file_id']
            elif type == 'voice':
                tag['content'] = msg['reply_to_message']['voice']['file_id']

            tags[name] = tag
            save_json('data/tags.json', tags)
            
            message = 'Added tag *#' + name + '* for that *' + type + '*.'
            send_message(msg['chat']['id'], message,
                         reply_to_message_id=msg['message_id'],
                         parse_mode="Markdown")
        
    else:
        print 'found tag'
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
