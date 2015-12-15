# -*- coding: utf-8 -*-
from utils import *
from cleverbot import Cleverbot
from HTMLParser import HTMLParser

# If someone mentions the bot's username, it replies
commands = [('@' + bot['username'].lower())]

action = 'typing'
hidden = True

def run(msg):
    input = msg['text'].replace(bot['first_name'] + ' ', '')

    cb = Cleverbot()
    unescape = HTMLParser().unescape

    try:
        message = unescape(cb.ask(input))
    except:
        message = u'🙃'

    send_message(msg['chat']['id'], message, reply_to_message_id = msg['message_id'])

def process(msg):
    if ('reply_to_message' in msg and
        'text' in msg['reply_to_message'] and
        'text' in msg):

        if (str(msg['chat']['id']) in groups and
            groups[str(msg['chat']['id'])]['special'] != 'log'):
            if (msg['reply_to_message']['from']['id'] == bot['id'] and
                    not msg['text'].startswith(config['command_start'])):
                msg['text'] = '@' + bot['username'] + ' ' + msg['text']

    if ('text' in msg and
        msg['chat']['type'] == 'private' and
        not msg['text'].startswith(config['command_start'])):
        msg['text'] = '@' + bot['username'] + ' ' + msg['text']
