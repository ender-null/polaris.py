from core.utils import *
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
    bot.id = msg['peer_id']

def convert_message(msg):
    id = msg['id']
    if msg['receiver']['type'] == 'user':
        receiver = User
        receiver.id = int(msg['receiver']['peer_id'])
        receiver.first_name = msg['receiver']['first_name']
        if 'last_name' in msg['receiver']:
            receiver.last_name = msg['receiver']['last_name']
        if 'username' in msg['receiver']:
            receiver.username = msg['receiver']['username']
    else:
        receiver = Group
        receiver.id = - int(msg['receiver']['peer_id'])
        receiver.title = msg['receiver']['title']
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
        type = msg['media']['type']
        content = msg['id']
        if 'caption' in msg['media']:
            extra = msg['media']['caption']
        else:
            extra = None
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
        if message.markup == 'Markdown':
            message.content = remove_markdown(message.content)
        tgsender.send_msg(peer(message.receiver.id), message.content)
    elif message.type == 'photo':
        tgsender.send_photo(peer(message.receiver.id), message.content.name, message.extra)
    elif message.type == 'audio':
        tgsender.send_audio(peer(message.receiver.id), message.content.name)
    elif message.type == 'document':
        tgsender.send_document(peer(message.receiver.id), message.content.name)
    elif message.type == 'sticker':
        tgsender.send_file(peer(message.receiver.id), message.content.name)
    elif message.type == 'video':
        tgsender.send_video(peer(message.receiver.id), message.content.name, message.extra)
    elif message.type == 'voice':
        tgsender.send_audio(peer(message.receiver.id), message.content.name)
    elif message.type == 'location':
        tgsender.send_location(peer(message.receiver.id), message.content, message.extra)
    else:
        print('UNKNOWN MESSAGE TYPE: ' + message.type)

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
                print('>> [{0} << {2}] {1}'.format(message.receiver.first_name, message.content[:10], message.sender.first_name))
            else:
                print('>> [{0} << {2}] {1}'.format(message.receiver.title, message.content[:10], message.sender.first_name))
        else:
            if message.receiver.id > 0:
                print('>> [{0} << {2}] <{1}>'.format(message.receiver.first_name, message.type, message.sender.first_name))
            else:
                print('>> [{0} << {2}] <{1}>'.format(message.receiver.title, message.type, message.sender.first_name))
        send_message(message)


def init():
    print('\nInitializing Telegram-CLI...')
    get_me()
    print('\tUsing: [{2}] {0} (@{1})'.format(bot.first_name, bot.username, bot.id))

    Thread(target=inbox_listen, name='Inbox Listener').start()
    Thread(target=outbox_listen, name='Outbox Listener').start()
