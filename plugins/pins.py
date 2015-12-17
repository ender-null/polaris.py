# -*- coding: utf-8 -*-
from utils import *

pins = load_json('data/pins.json')
def get_pins(pins):
    commands = [
        '^pin',
        '^unpin',
        '^pins',
        '^content'
    ]
    for pin, data in pins.items():
        commands.append('#' + pin)
    return commands


commands = get_pins(pins)
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
    if (get_command(msg['text']) == 'pin'
        or get_command(msg['text']) == 'content'):

        if get_command(msg['text']) == 'pin':
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
                    content = msg['reply_to_message']['text']
                else:
                    content = None
            else:
                content = None

            # Check if tag exists
            if name in pins:
                message = 'The pin *#' + name + '* exists!'
                if msg['from']['id'] == pins[name]['creator']:
                    message += '\nBut you can delete it with `' + config['command_start'] + 'unpin ' + name + '`.'
                else:
                    message += '\nBut you are not allowed to delete it.'
                return send_message(msg['chat']['id'], message, parse_mode="Markdown")
            if not type:
                return send_error(msg, 'argument')
            if not type in types:
                message = 'You need to provide a valid type.'
                return send_message(msg['chat']['id'], message, parse_mode="Markdown")
            if content:
                pin = OrderedDict()
                pin['creator'] = msg['from']['id']
                pin['type'] = type
                pin['content'] = content
                pins[name] = pin
                save_json('data/pins.json', pins)

                message = 'Added pin *#' + name + '* for that *' + type + '*.'
                return send_message(msg['chat']['id'], message,
                             reply_to_message_id=msg['message_id'],
                             parse_mode="Markdown")

            message = 'Reply with a *' + type + '* for the pin *#' + name + '*'

            force_reply_json = {'force_reply': True, 'selective': True}
            force_reply = json.dumps(force_reply_json)

            send_message(msg['chat']['id'], message,
                         reply_to_message_id=msg['message_id'],
                         reply_markup=force_reply,
                         parse_mode="Markdown")
        elif get_command(msg['text']) == 'content':
            name = first_word(msg['reply_to_message']['text'], 8).replace('#', '')
            type = first_word(msg['reply_to_message']['text'], 4)

            pin = OrderedDict()
            pin['creator'] = msg['from']['id']
            pin['type'] = type
            if type == 'text':
                pin['content'] = msg['text'].replace(first_word(msg['text']) + ' ', '')
            elif type == 'audio':
                pin['content'] = msg['audio']['file_id']
            elif type == 'document':
                pin['content'] = msg['document']['file_id']
            elif type == 'photo':
                pin['content'] = msg['photo'][-1]['file_id']
            elif type == 'sticker':
                pin['content'] = msg['sticker']['file_id']
            elif type == 'video':
                pin['content'] = msg['video']['file_id']
            elif type == 'voice':
                pin['content'] = msg['voice']['file_id']

            pin[name] = pin
            save_json('data/pins.json', pins)

            message = 'Added pin *#' + name + '* for that *' + type + '*.'
            send_message(msg['chat']['id'], message,
                         reply_to_message_id=msg['message_id'],
                         parse_mode="Markdown")
    elif get_command(msg['text']) == 'unpin':
        input = get_input(msg['text'])
        if not input:
            doc = get_doc(commands, parameters, description)
            return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

        name = first_word(input)
        if name in pins:
            if msg['from']['id'] == pins[name]['creator'] or is_admin(msg):
                del pins[name]
                save_json('data/pins.json', pins)
                message = '\nYou removed the pin *#' + name + '*.'
            else:
                return send_error(msg, 'permission')
        else:
            message = 'The pin *' + name + '* is not set.'
        send_message(msg['chat']['id'], message, parse_mode="Markdown")
    elif get_command(msg['text']) == 'pins':
        #taglist = [None] * len(pins)
        #i = 0
        #for pins, data in pins.items():
        #    pins[i] = '\n\t#' + str(pin) + ' | ' + data['type'] + ' | ' + str(data['creator'])
        #    i += 1
        #i = 0
        #while i <= len(pins):
        #    message = ''
        #    while i < 40:
        #        message += pins[i]
        #    send_message(msg['chat']['id'], message, parse_mode="Markdown")
        #    i += 40
        message = '`#GiTGuD`'
        send_message(msg['chat']['id'], message, parse_mode="Markdown")
    else:
        for pin, data in pins.items():
            if '#' + pin.lower() in msg['text'].lower():
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
    pins = load_json('data/pins.json', True)
