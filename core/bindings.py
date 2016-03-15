from core.shared import *
import sys, traceback


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


def send_document(m, document, caption=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, document, 'document', extra=caption)
    else:
        message = Message(None, bot, m.receiver, document, 'document', extra=caption)
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
    if str(m.receiver.id)[1:].startswith('100'):
        result = bot.wrapper.tgsender.channel_invite(bot.wrapper.peer(m.receiver.id), bot.wrapper.peer(bot.wrapper.get_id(user)))
    else:
        result = bot.wrapper.tgsender.chat_add_user(bot.wrapper.peer(m.receiver.id), bot.wrapper.peer(bot.wrapper.get_id(user)))
    print(result)
    if hasattr(result, 'result') and result.result == 'FAIL':
        if result.error.split()[-1] == 'PEER_FLOOD':
            return None
        return False
    else:
        return True


def kick_user(m, user):
    print(bot.wrapper.peer(m.receiver.id) + '/' + bot.wrapper.peer(bot.wrapper.get_id(user)))
    if str(m.receiver.id)[1:].startswith('100'):
        result = bot.wrapper.tgsender.channel_kick(bot.wrapper.peer(m.receiver.id), bot.wrapper.peer(bot.wrapper.get_id(user)))
    else:
        result = bot.wrapper.tgsender.chat_del_user(bot.wrapper.peer(m.receiver.id), bot.wrapper.peer(bot.wrapper.get_id(user)))
        
    print(result)
    
    if hasattr(result, 'result') and result.result == 'FAIL':
        if result.error.split()[-1] == 'CHAT_ADMIN_REQUIRED':
            print('return None')
            return None
        print('return False')
        return False
    else:
        return True
    
    
def user_info(user):
    if config.wrapper == 'tg':
        result = bot.wrapper.tgsender.user_info(bot.wrapper.peer(bot.wrapper.get_id(user)))
        if hasattr(result, 'print_name'):
            return result['print_name'].replace('_', ' ')
        else:
            return user
    else:
        return user

def send_alert(m, text):
    for chat in config.chats:
        type, id, role = chat.split('/')
        if m.type == 'text' and role == 'alerts' and m.sender.id != int(id):
            message = '<code>%s</code>' % text
            
            receiver = Group()
            receiver.id = - int('100' + id)
            receiver.title = role

            if m.receiver.id > 0:
                message = Message(None, receiver, m.sender, message, markup='HTML')
            else:
                message = Message(None, m.sender, receiver, message, markup='HTML')
            outbox.put(message)
    
def send_exception(m):
    for chat in config.chats:
        type, id, role = chat.split('/')
        if m.type == 'text' and role == 'alerts' and m.sender.id != int(id):
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
            
            if type == 'user':
                receiver = User()
                receiver.id = id
                receiver.first_name = role
            elif type == 'channel':
                receiver = Group()
                receiver.id = - int('100' + id)
                receiver.title = role
            else:
                receiver = Group()
                receiver.id = - id
                receiver.title = role

            if m.receiver.id > 0:
                message = Message(None, receiver, m.sender, message, markup='HTML')
            else:
                message = Message(None, m.sender, receiver, message, markup='HTML')
            outbox.put(message)

    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, '<code>%s</code>' % lang.errors.exception, 'text', markup='HTML', extra=False)
    else:
        message = Message(None, bot, m.receiver, '<code>%s</code>' % lang.errors.exception, 'text', markup='HTML', extra=False)
    outbox.put(message)
