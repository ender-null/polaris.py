from core.shared import *
from threading import Thread
from pytg.receiver import Receiver
from pytg.sender import Sender
from pytg.utils import coroutine
import json

tgreceiver = Receiver(host="localhost", port=4458)
tgsender = Sender(host="localhost", port=4458)


# Telegram-CLI bindings

def peer(chat_id):
    if chat_id > 0:
        peer = 'user#id' + str(chat_id)
    else:
        peer = 'chat#id' + str(chat_id)[1:]
    return peer


def get_me():
    msg = tgsender.get_self()
    bot.first_name = msg['first_name']
    bot.username = msg['username']
    bot.id = msg['id']


def send_message(message):
    if message.type == 'text':
        tgsender.send_msg(peer(message.receiver.id), message.content)
    elif message.type == 'photo':
        tgsender.send_photo(peer(message.receiver.id), message.content.name, message.extra)


def inbox_listen():
    print('\tStarting inbox daemon...')
    last_update = 0

    @coroutine
    def listener():
        while (True):
            msg = (yield)

            if (msg['event'] == 'message' and msg['own'] == False):
                id = msg['id']
                if msg['receiver']['type'] == 'user':
                    receiver = User
                    receiver.first_name = msg['receiver']['first_name']
                    if hasattr(msg['receiver'], 'last_name'):
                        receiver.last_name = msg['receiver']['last_name']
                    receiver.username = msg['receiver']['username']
                    receiver.id = int(msg['receiver']['peer_id'])
                else:
                    receiver = Group
                    receiver.title = msg['receiver']['title']
                    receiver.id = - int(msg['receiver']['peer_id'])
                sender = User
                sender.id = int(msg['sender']['peer_id'])
                sender.first_name = msg['sender']['first_name']
                if 'last_name' in msg['sender']:
                    sender.last_name = msg['sender']['last_name']
                if 'username' in msg['sender']:
                    sender.username = msg['sender']['username']
                if 'text' in msg:
                    content = msg['text']
                date = msg['date']

                # Gets the type of the message
                if 'text' in msg:
                    type = 'text'
                else:
                    type = None

                # Generates another message object for the original message if the reply.
                if 'reply_id' in msg:
                    reply_msg = tgsender.message_get(msg['reply_id'])

                    reply_id = reply_msg['id']
                    if reply_msg['receiver']['type'] == 'user':
                        reply_receiver = User
                        reply_receiver.first_name = reply_msg['receiver']['first_name']
                        if 'last_name' in reply_msg['sender']:
                            reply_receiver.last_name = reply_msg['receiver']['last_name']
                        if 'username' in reply_msg['sender']:
                            reply_receiver.username = reply_msg['receiver']['username']
                        reply_receiver.id = int(reply_msg['receiver']['peer_id'])
                    else:
                        reply_receiver = Group
                        reply_receiver.title = reply_msg['receiver']['title']
                        reply_receiver.id = - int(reply_msg['receiver']['peer_id'])
                    reply_sender = User
                    reply_sender.id = int(reply_msg['sender']['peer_id'])
                    reply_sender.first_name = reply_msg['sender']['first_name']
                    if 'last_name' in reply_msg['sender']:
                        reply_sender.last_name = reply_msg['sender']['last_name']
                    if 'username' in reply_msg['sender']:
                        reply_sender.username = reply_msg['sender']['username']
                    if 'text' in reply_msg:
                        reply_content = reply_msg['text']
                    reply_date = reply_msg['date']

                    # Gets the type of the message
                    if 'text' in reply_msg:
                        reply_type = 'text'
                    else:
                        reply_type = None

                    reply = Message(reply_id, reply_sender, reply_receiver, reply_content, reply_type,
                                    reply_date)
                else:
                    reply = None

                message = Message(id, sender, receiver, content, type, date, reply)
                inbox.put(message)

    tgreceiver.start()
    tgreceiver.message(listener())


def outbox_listen():
    while (True):
        message = outbox.get()
        if message.type == 'text':
            print('OUTBOX: ' + message.content)
        else:
            print('OUTBOX: [{0}]'.format(message.type))
        send_message(message)


inbox_listener = Thread(target=inbox_listen, name='Inbox Listener')
outbox_listener = Thread(target=outbox_listen, name='Outbox Listener')


def init():
    print('\nInitializing Telegram-CLI...')
    get_me()
    print('\tUsing: {0} (@{1})'.format(bot.first_name, bot.username))

    inbox_listener.start()
    outbox_listener.start()
