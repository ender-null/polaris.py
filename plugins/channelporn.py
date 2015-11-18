# -*- coding: utf-8 -*-
from utilies import *


commands = ['']

hidden = True


def run(msg):
        if (msg['chat']['id'] == -27616291 and
                not msg['text'] and
                not hasattr(msg, 'text') and
                not hasattr(msg, 'new_chat_participant') and
                not hasattr(msg, 'left_chat_participant') and
                not hasattr(msg, 'new_chat_title') and
                not hasattr(msg, 'new_chat_photo') and
                not hasattr(msg, 'delete_chat_photo') and
                not hasattr(msg, 'group_chat_created') and
                not hasattr(msg, 'sticker') and
                not hasattr(msg, 'audio') and
                not hasattr(msg, 'voice')):

            forward_message('@porndb',  msg['chat']['id'], msg['message_id'])
