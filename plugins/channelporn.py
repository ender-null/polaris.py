# -*- coding: utf-8 -*-
from utilies import *

commands = ['']

hidden = True
nonstop = True

def run(msg):
        if (msg['chat']['id'] == -27616291 and
                not 'text' in msg and
                not 'new_chat_participant' in msg and
                not 'left_chat_participant' in msg and
                not 'new_chat_title' in msg and
                not 'new_chat_photo' in msg and
                not 'delete_chat_photo' in msg and
                not 'group_chat_created' in msg and
                not 'sticker' in msg and
                not 'audio' in msg and
                not 'voice' in msg):
            print('forwarded')
            forward_message('@porndb',  msg['chat']['id'], msg['message_id'])
