from core.shared import *
from threading import Thread
from pytg.receiver import Receiver
from pytg.sender import Sender
from pytg.utils import coroutine
import json

receiver = Receiver(host="localhost", port=4458)
sender = Sender(host="localhost", port=4458)


# Telegram-CLI bindings

def peer(chat_id):
    if chat_id > 0:
        peer = 'user#id' + str(chat_id)
    else:
        peer = 'chat#id' + str(chat_id)[1:]
    return peer


def get_me():
    msg = sender.get_self()
    bot.first_name = msg['first_name']
    bot.username = msg['username']
    bot.id = msg['id']


def send_message(message):
    if message.type == 'text':
        sender.send_msg(peer(message.receiver.id), message.content)


def inbox_listen():
    print('\tStarting inbox daemon...')
    last_update = 0

    @coroutine
    def listener():
        while (True):
            msg = (yield)

            if (msg['event'] == 'message' and msg['own'] == False):
                if msg['receiver']['type'] == 'user':
                    receiver = User
                    receiver.first_name = msg['receiver']['first_name']
                    if hasattr(msg['receiver'], 'last_name'):
                        receiver.last_name = msg['receiver']['last_name']
                    receiver.username = msg['receiver']['username']
                    receiver.id = msg['receiver']['id']
                else:
                    receiver = Group
                    receiver.title = msg['receiver']['title']
                    receiver.id = - msg['receiver']['id']
                sender = User
                sender.id = msg['sender']['id']
                sender.first_name = msg['sender']['first_name']
                if hasattr(msg['sender'], 'last_name'):
                    sender.last_name = msg['sender']['last_name']
                sender.username = msg['sender']['username']
                content = msg['text']
                date = msg['date']

                message = Message(None, sender, receiver, content, date)
                inbox.put(message)

    receiver.start()
    receiver.message(listener())


def outbox_listen():
    while (True):
        message = outbox.get()
        print('OUTBOX: ' + message.content)
        send_message(message)


inbox_listener = Thread(target=inbox_listen, name='Inbox Listener')
outbox_listener = Thread(target=outbox_listen, name='Outbox Listener')


def init():
    print('\nInitializing Telegram-CLI...')
    get_me()
    print('\tUsing: {0} (@{1})'.format(bot.first_name, bot.username))

    inbox_listener.start()
    outbox_listener.start()
