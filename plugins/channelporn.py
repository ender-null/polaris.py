# -*- coding: utf-8 -*-
from utilies import *

commands = ['']

hidden = True
nonstop = True

def run(msg):
    ids = [-27616291, -951476]
    if (msg['chat']['id'] in ids and
        not msg['text'] != '' and
        not 'new_chat_participant' in msg and
        not 'left_chat_participant' in msg and
        not 'new_chat_title' in msg and
        not 'new_chat_photo' in msg and
        not 'delete_chat_photo' in msg and
        not 'group_chat_created' in msg and
        not 'sticker' in msg and
        not 'audio' in msg and
        not 'voice' in msg):
        
        send_alert('Forward from ' + msg['from']['first_name'])
        forward_message('@porndb',  msg['chat']['id'], msg['message_id'])