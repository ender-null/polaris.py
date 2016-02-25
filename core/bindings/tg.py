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

def convert_message(msg):
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
    date = msg['date']

    # Gets the type of the message
    if 'text' in msg:
        type = 'text'
        content = msg['text']
        extra = None
    elif 'media' in msg:
        print(msg['media'])
        if 'photo' in msg['media']:
            type = 'photo'
            content = None
            extra = msg['media']['caption']
    else:
        type = None
        content = None
        extra = None

    # Generates another message object for the original message if the reply.
    if 'reply_id' in msg:
        reply_msg = tgsender.message_get(msg['reply_id'])
        reply = convert_message(reply_msg)
    else:
        reply = None

    return Message(id, sender, receiver, content, type, date, reply, extra)

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
        while (started):
            msg = (yield)

            if (msg['event'] == 'message' and msg['own'] == False):
                message = convert_message(msg)
                inbox.put(message)

    tgreceiver.start()
    tgreceiver.message(listener())


def outbox_listen():
    while (started):
        message = outbox.get()
        if message.type == 'text':
            if message.receiver.id > 0:
                print('OUTBOX: [{0}] {1}'.format(message.receiver.first_name, message.content))
            else:
                print('OUTBOX: [{0}] {1}'.format(message.receiver.title, message.content))
        else:
            if message.receiver.id > 0:
                print('OUTBOX: [{0}] <{1}>'.format(message.receiver.first_name, message.type))
            else:
                print('OUTBOX: [{0}] <{1}>'.format(message.receiver.title, message.type))
        send_message(message)


def init():
    print('\nInitializing Telegram-CLI...')
    get_me()
    print('\tUsing: {0} (@{1})'.format(bot.first_name, bot.username))

    Thread(target=inbox_listen, name='Inbox Listener').start()
    Thread(target=outbox_listen, name='Outbox Listener').start()
