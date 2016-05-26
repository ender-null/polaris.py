from core.utils import *
from pytg.receiver import Receiver
from pytg.sender import Sender
from pytg.utils import coroutine
import json

tgreceiver = Receiver(host="localhost", port=config.keys.tg_cli_port)
tgsender = Sender(host="localhost", port=config.keys.tg_cli_port)


# Telegram-CLI bindings
def peer(chat_id):
    if chat_id > 0:
        peer = 'user#id' + str(chat_id)
    else:
        if str(chat_id)[1:].startswith('100'):
            peer = 'channel#id' + str(chat_id)[4:]
        else:
            peer = 'chat#id' + str(chat_id)[1:]
    return peer


def user_id(username):
    if username.startswith('@'):
        command = 'resolve_username ' + username[1:]
        resolve = tgsender.raw(command)
        dict = DictObject(json.loads(resolve))
    else:
        dict = tgsender.user_info(username)

    if 'peer_id' in dict:
        return dict.peer_id
    else:
        return False


def get_id(user):
    if isinstance(user, int):
        return user
    
    if user.isdigit():
        id = int(user)
    else:
        id = int(user_id(user))

    return id
    
def escape(string):
    if string is None:
        return None
        
    CHARS_UNESCAPED = ["\\", "\n", "\r", "\t", "\b", "\a", "'"]
    CHARS_ESCAPED = ["\\\\", "\\n", "\\r", "\\t", "\\b", "\\a", "\\'"]
    
    for i in range(0, 7):
        string = string.replace(CHARS_UNESCAPED[i], CHARS_ESCAPED[i])
    return string.join(["'", "'"])  # wrap with single quotes.

# Standard methods for bindings
def get_me():
    msg = tgsender.get_self()
    bot.first_name = msg.first_name
    bot.username = msg.username
    bot.id = msg.peer_id

def kick_chat_member(chat, user):
    if str(chat).startswith('-100'):
            result = tgsender.channel_kick(peer(chat), peer(get_id(user)))
        else:
            result = tgsender.chat_del_user(peer(chat), peer(get_id(user)))
    except:
        error = str(sys.exc_info()[1]).split()[4].rstrip("'")
    else:
        if hasattr(result, 'result') and result.result == 'FAIL':
            error = result.error.split()[-1]
        else:
            return True
            
    if error == 'CHAT_ADMIN_REQUIRED':
        raise PolarisExceptions.NotAdminException()
    else:
        raise PolarisExceptions.FailedException()
        
def unban_chat_member(chat, user):
    pass
    

def chat_info(user):
    result = bot.wrapper.tgsender.user_info(bot.wrapper.peer(bot.wrapper.get_id(user)))
    if hasattr(result, 'print_name'):
        return result
    else:
        return user

def convert_message(msg):
    id = msg['id']
    if msg.receiver.type == 'user':
        receiver = User()
        receiver.id = int(msg.receiver.peer_id)
        receiver.first_name = msg.receiver.first_name
        if 'first_name' in msg.receiver:
            receiver.first_name = msg.receiver.first_name
        if 'last_name' in msg.receiver:
            receiver.last_name = msg.receiver.last_name
        if 'username' in msg.receiver:
            receiver.username = msg.receiver.username
    else:
        receiver = Group()
        if msg.receiver.type == 'channel':
            receiver.id = - int('100' + str(msg.receiver.peer_id))
        else:
            receiver.id = - int(msg.receiver.peer_id)
        receiver.title = msg.receiver.title
        
    if msg.sender.type == 'user':
        sender = User()
        sender.id = int(msg.sender.peer_id)
        sender.first_name = msg.sender.first_name
        if 'first_name' in msg.sender:
            sender.first_name = msg.sender.first_name
        if 'last_name' in msg.sender:
            sender.last_name = msg.sender.last_name
        if 'username' in msg.sender:
            sender.username = msg.sender.username
    else:
        sender = Group()
        if msg.sender.type == 'channel':
            sender.id = - int('100' + str(msg.sender.peer_id))
        else:
            sender.id = - int(msg.sender.peer_id)
        sender.title = msg.sender.title
        
    date = msg.date

    # Gets the type of the message
    if 'text' in msg:
        type = 'text'
        content = msg.text
        extra = None
    elif 'media' in msg:
        type = msg.media.type
        content = msg.id
        if 'caption' in msg.media:
            extra = msg.media.caption
        else:
            extra = None
    elif msg.event == 'service':
        type = 'service'
        if msg.action.type == 'chat_del_user':
            content = 'left_user'
            extra = msg.action.user.peer_id
        elif msg.action.type == 'chat_add_user':
            content = 'join_user'
            extra = msg.action.user.peer_id
        elif msg.action.type == 'chat_add_user_link':
            content = 'join_user'
            extra = msg.sender.peer_id
        else:
            type = None
            content = None
            extra = None
    else:
        type = None
        content = None
        extra = None

    # Generates another message object for the original message if the reply.
    if 'reply_id' in msg:
        reply_msg = tgsender.message_get(msg.reply_id)
        reply = convert_message(reply_msg)
        
    else:
        reply = None

    return Message(id, sender, receiver, content, type, date, reply, extra)


def send_message(message):
    if message.type == 'text':
        tgsender.send_typing(peer(message.receiver.id), 1)

        if message.markup == 'Markdown':
            message.content = remove_markdown(message.content)
        elif message.markup == 'HTML':
            message.content = remove_html(message.content)

        try:
            tgsender.send_msg(peer(message.receiver.id), message.content, enable_preview=message.extra)
        except:
            tgsender.raw('post ' + peer(message.receiver.id) + ' ' + escape(message.content), enable_preview=message.extra)

    elif message.type == 'photo':
        tgsender.send_typing(peer(message.receiver.id), 1) # 7
        try:
            tgsender.send_photo(peer(message.receiver.id), message.content.name, message.extra)
        except:
            tgsender.raw('post_photo %s %s %s' % (peer(message.receiver.id), message.content.name, escape(message.extra)))
        
    elif message.type == 'audio':
        tgsender.send_typing(peer(message.receiver.id), 1) # 6
        try:
            tgsender.send_audio(peer(message.receiver.id), message.content.name)
        except:
            tgsender.raw('post_audio %s %s %s' % (peer(message.receiver.id), message.content.name, escape(message.extra)))
        
    elif message.type == 'document':
        tgsender.send_typing(peer(message.receiver.id), 1) # 8
        try:
            # tgsender.send_document(peer(message.receiver.id), message.content.name, message.extra)
            tgsender.send_document(peer(message.receiver.id), message.content.name, escape(message.extra))
        except:
            tgsender.raw('post_document %s %s %s' % (peer(message.receiver.id), message.content.name, escape(message.extra)))

    elif message.type == 'sticker':
        tgsender.send_file(peer(message.receiver.id), message.content.name)
        
    elif message.type == 'video':
        tgsender.send_typing(peer(message.receiver.id), 1) # 4
        try:
            tgsender.send_video(peer(message.receiver.id), message.content.name)
        except:
            tgsender.raw('post_video %s %s' % (peer(message.receiver.id), message.content.name))
        
    elif message.type == 'voice':
        tgsender.send_typing(peer(message.receiver.id), 5)
        try:
            tgsender.send_audio(peer(message.receiver.id), message.content.name)
        except:
            tgsender.raw('post_audio %s %s' % (peer(message.receiver.id), message.content.name))
        
    elif message.type == 'location':
        tgsender.send_typing(peer(message.receiver.id), 1) # 9
        tgsender.send_location(peer(message.receiver.id), message.content, message.extra)
            
    else:
        print('UNKNOWN MESSAGE TYPE: ' + message.type)


def inbox_listener():
    @coroutine
    def listener():
        while (True):
            msg = (yield)
            if (msg.event == 'message' and msg.own == False) or msg.event == 'service':
                message = convert_message(msg)
                inbox.put(message)
                
                try:
                    if message.receiver.id > 0:
                        tgsender.mark_read(peer(message.sender.id))
                    else:
                        tgsender.mark_read(peer(message.receiver.id))
                except:
                    pass

    tgreceiver.start()
    tgreceiver.message(listener())
