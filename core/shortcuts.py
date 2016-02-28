import sys, traceback

from core.shared import *

def send_message(m, text, preview=False, markup=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, text, 'text', markup=markup, extra=preview)
    else:
        message = Message(None, bot, m.receiver, text, 'text', markup=markup, extra=preview)
    outbox.put(message)


def send_photo(m, photo, caption=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, photo, 'photo', extra=caption)
    else:
        message = Message(None, bot, m.receiver, photo, 'photo', extra=caption)
    outbox.put(message)


def send_document(m, document):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, document, 'document')
    else:
        message = Message(None, bot, m.receiver, document, 'document')
    outbox.put(message)


def send_video(m, video, caption=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, video, 'video', extra=caption)
    else:
        message = Message(None, bot, m.receiver, video, 'video', extra=caption)
    outbox.put(message)


def send_audio(m, audio, title=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, audio, 'audio', extra=title)
    else:
        message = Message(None, bot, m.receiver, audio, 'audio', extra=title)
    outbox.put(message)


def send_voice(m, voice):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, voice, 'voice')
    else:
        message = Message(None, bot, m.receiver, voice, 'voice')
    outbox.put(message)


def send_sticker(m, sticker):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, sticker, 'sticker')
    else:
        message = Message(None, bot, m.receiver, sticker, 'sticker')
    outbox.put(message)


def invite_user(m, user):
    message = Message(None, bot, m.receiver, 'invite_user', 'status', extra=user)
    outbox.put(message)


def kick_user(m, user):
    message = Message(None, bot, m.receiver, 'kick_user', 'status', extra=user)
    outbox.put(message)


def show_message(m):
    text = 'Message info:\n'
    text += 'sender.id: ' + m.sender.id + '\n'
    text += 'sender.first_name: ' + m.sender.first_name + '\n'
    text += 'receiver.id: ' + m.receiver.id + '\n'
    text += 'receiver.first_name: ' + m.receiver.first_name + '\n'
    text += 'type: ' + m.type + '\n'
    text += 'extra: ' + m.extra + '\n'
    if m.reply:
        text += 'reply.sender.id: ' + m.reply.sender.id + '\n'
        text += 'reply.sender.first_name: ' + m.reply.sender.first_name + '\n'
        text += 'reply.receiver.id: ' + m.reply.receiver.id + '\n'
        text += 'reply.receiver.first_name: ' + m.reply.receiver.first_name + '\n'
        text += 'reply.type: ' + m.reply.type + '\n'
        text += 'reply.extra: ' + m.reply.extra + '\n'


    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, text, 'text')
    else:
        message = Message(None, bot, m.receiver, text, 'text')
    outbox.put(message)


def send_exception(m):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb, 4)
    message = '\n`' + str(exc_type) + '`'
    message += '\n\n`' + str(exc_obj) + '`'
    for row in tb:
        message += '\n'
        for val in row:
            message += '`' + str(val) + '`, '

    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, message, markup='Markdown')
    else:
        message = Message(None, bot, m.receiver, message, markup='Markdown')
    outbox.put(message)