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

    
def answer_inline_query(m, results, offset=None):
    message = Message(m.id, bot, m.receiver, results, 'inline_results', extra=offset)
    outbox.put(message)

def invite_user(m, user):
    message = Message(None, bot, m.receiver, 'invite_user', 'status', extra=user)
    outbox.put(message)


def kick_user(m, user):
    message = Message(None, bot, m.receiver, 'kick_user', 'status', extra=user)
    outbox.put(message)


def send_exception(m):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb, 4)
    message = '<code>' + str(exc_type.__name__)
    message += '\n\n' + str(exc_obj)
    for row in tb:
        message += '\n'
        for val in row:
            message += str(val) + ', '
        message += '\n'
    message += '</code>'

    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, message, markup='HTML')
    else:
        message = Message(None, bot, m.receiver, message, markup='HTML')
    outbox.put(message)
