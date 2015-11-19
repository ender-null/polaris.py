# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *

tags = load_json('data/tags.json')
	
def get_tags(tags, size):
    i = 0
    commands = [None] * size
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
    print 'triggered'

    if get_command(msg['text']) == 'tag':
        input = get_input(msg['text'])

        if not input:
            doc = get_doc(commands, parameters, description)
            return send_message(msg['chat']['id'], doc, parse_mode="Markdown")
    else:
        for tag, data in tags.items():
            if '#' + tag in msg['text']:
                print 'found match'
                if data['type'] == 'text':
                    send_message(msg['chat']['id'], data['content'])
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
