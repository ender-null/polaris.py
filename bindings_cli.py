from pytg.receiver import Receiver
from pytg.sender import Sender
import json

receiver = Receiver(host="localhost", port=4458)
sender = Sender(host="localhost", port=4458)

def peer(chat_id):
    if chat_id > 0:
        peer = 'user#id' + str(chat_id)
    else:
        peer = 'chat#id' + str(chat_id)[1:]
    return peer

def user_id(username):
    command = 'resolve_username ' + username
    resolve = sender.raw(command)
    dict = json.loads(resolve)
    if 'peer_id' in dict:
        return dict['peer_id']
    else:
        return False

# sending messages
def send_message(chat_id, text, reply_to_message_id=None):
    cid = peer(chat_id)
    if reply_to_message_id:
        return sender.reply_text(cid, text)
    else:
        return sender.send_text(cid, text)

def forward_message(chat_id, message_id):
    cid = peer(chat_id)
    return sender.fwd(cid, message_id)

def send_photo(chat_id, photo, caption=None, reply_to_message_id=None):
    cid = peer(chat_id)
    if reply_to_message_id:
        return sender.reply_photo(cid, photo.name, caption)
    else:
        return sender.send_photo(cid, photo.name)

def send_audio(chat_id, audio, reply_to_message_id=None):
    cid = peer(chat_id)
    if reply_to_message_id:
        return sender.reply_audio(cid, audio.name)
    else:
        return sender.send_audio(cid, audio.name)

def send_document(chat_id, document, reply_to_message_id=None):
    pass
    
def send_sticker(chat_id, sticker, reply_to_message_id=None):
    pass

def send_video(chat_id, video, duration=None, caption=None, reply_to_message_id=None):
    pass

def send_voice(chat_id, voice, duration=None, reply_to_message_id=None):
    pass

def send_location(chat_id, latitude, longitude, reply_to_message_id=None):
    pass

# chats
def chat_info(chat_id):
    cid = peer(chat_id)
    print(sender.chat_info(cid))
    #return sender.chat_info(cid)

def chat_set_photo(chat_id, photo):
    cid = peer(chat_id)
    return sender.chat_set_photo(cid, photo.name)

def chat_add_user(chat_id, user, msgs_to_forward=100):
    cid = peer(chat_id)
    uid = peer(user)
    return sender.chat_add_user(cid, uid, msgs_to_forward)

def chat_del_user(chat_id, user):
    cid = peer(chat_id)
    uid = peer(user)
    return sender.chat_del_user(cid, uid)

def chat_rename(chat_id, name):
    cid = peer(chat_id)
    return sender.chat_rename(cid, name)

def create_group_chat(name, user):
    uid = peer(user)
    return sender.create_group_chat(name, uid)
    
def import_chat_link(hash):
    return sender.import_chat_link(hash)

def export_chat_link(chat_id):
    cid = peer(chat_id)
    return sender.export_chat_link(cid)

# contact related
def contacts_search(name, limit=None):
    return sender.contacts_search(name)

# own profile related
def set_profile_name(first_name, last_name):
    return sender.set_profile_name(first_name, last_name)

def set_username(username):
    return sender.set_username(username)

def set_profile_photo(photo):
    return sender.set_profile_photo(photo.name)

def status_online():
    return sender.status_online()

def status_offline():
    return sender.status_offline()

def export_card():
    return sender.export_card()

# other
def raw(command):
    return sender.raw(command)
