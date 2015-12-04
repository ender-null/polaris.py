# -*- coding: utf-8 -*-
from utilies import *

hidden = True

def process(msg):
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
        
        if 'username' in msg['from']:
            sender = '@' + msg['from']['username']
        else:
            sender = msg['from']['first_name']
        
        if 'photo' in msg:
            send_alert('Forwarded \n`{0}`\nfrom {1} to @porndb.'.format(msg['photo'][0]['file_id'], sender))
            send_photo('@porndb',  msg['photo'][0]['file_id'])
        elif 'document' in msg:
            send_alert('Forwarded \n`{0}`\nfrom {1} to @porndb.'.format(msg['document']['file_id'], sender))
            send_document('@porndb', msg['document']['file_id'])