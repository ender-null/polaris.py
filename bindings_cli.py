from pytg.receiver import Receiver
from pytg.sender import Sender 

receiver = Receiver(host="localhost", port=4458)
sender = Sender(host="localhost", port=4458)

def peer(chat_id):
    if chat_id > 0:
        peer = 'user#id' + str(chat_id)
    else:
        peer = 'chat#id' + str(chat_id)[1:]
    return peer


def send_message(chat_id, text,
                 reply_to_message_id=None):
    
    if reply_to_message_id:
        return sender.reply_text(peer(chat_id), text)
    else:
        return sender.send_text(peer(chat_id), text)

def chat_info(chat_id):
    print sender.chat_info(peer(chat_id))
    #return sender.export_chat_link(peer(chat_id))
    
def chat_delete_user(chat_id, user):
    return sender.chat_del_user(peer(chat_id), peer(user))
    
def export_chat_link(chat_id):
    return sender.export_chat_link(peer(chat_id))