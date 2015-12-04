# -*- coding: utf-8 -*-
from utilies import *
import cleverbot
from HTMLParser import HTMLParser

# If someone mentions the bot's first name, ignoring -chan or similar extensions.
commands = [bot['first_name'].split('-')[0].lower()]

description = 'Get list of basic information for all commands, or more detailed documentation on a specified command.'
action = 'typing'
hidden = True


def run(msg):
    print 'chatter'

    input = msg['text'].replace(bot['first_name'] + ' ', '')

    cb = cleverbot.Cleverbot()
    unescape = HTMLParser().unescape

    try:
        message = unescape(cb.ask(input))
    except:
        message = '...'

    send_message(msg['chat']['id'], message)

def process(msg):
    if ('reply_to_message' in msg and
        'text' in msg['reply_to_message'] and
        'text' in msg):

        if (str(msg['chat']['id']) in groups and
            groups[str(msg['chat']['id'])]['special'] != 'log'):
            if (msg['reply_to_message']['from']['id'] == bot['id'] and
                    not msg['text'].startswith(config['command_start'])):
                msg['text'] = bot['first_name'] + ' ' + msg['text']
            elif msg['text'].startswith(config['command_start']):
                msg['text'] += ' ' + msg['reply_to_message']['text']

    if ('text' in msg and
        msg['chat']['type'] == 'private' and
        not msg['text'].startswith(config['command_start'])):
        msg['text'] = bot['first_name'].split('-')[0] + ' ' + msg['text']