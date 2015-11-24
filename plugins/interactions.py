# -*- coding: utf-8 -*-
from utilies import *

commands = ['']
hidden = True
nonstop = True


def run(msg):
    input = msg['text'].lower()

    for interaction in locale[get_locale(msg['chat']['id'])]['interactions']:
        for trigger in locale[get_locale(msg['chat']['id'])]['interactions'][interaction]:
            trigger = tag_replace(trigger, msg)
            if re.match(trigger.lower(), input):
                interaction = tag_replace(interaction, msg)
                return send_message(msg['chat']['id'], interaction, parse_mode="Markdown")

def process(msg):
    if (config['process']['new_chat_participant'] and
        'new_chat_participant' in msg):
        if msg['new_chat_participant']['id'] != bot['id']:
            msg['text'] = '!new_chat_participant'
            msg['from'] = msg['new_chat_participant']
        else:
            msg['text'] = '/about'

    if (config['process']['left_chat_participant'] and
       'left_chat_participant' in msg):
        if msg['left_chat_participant']['id'] != bot['id']:
            msg['text'] = '!left_chat_participant'
            msg['from'] = msg['left_chat_participant']