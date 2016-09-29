from polaris.types import Message, Conversation, User
from polaris.utils import send_request
from six import string_types
from time import time
import requests, logging

def api_request(bot, api_method, params=None, headers=None, files=None):
    url = 'https://api.telegram.org/bot%s/%s' % (bot.config.bindings_token, api_method)

    try:
        return send_request(url, params, headers, files, post=True)
    except:
        return None

def get_me(bot):
    r = api_request(bot, 'getMe')
    return User(r.result.id, r.result.first_name, None, r.result.username)


def convert_message(msg):
    id = msg.message_id
    if msg.chat.id > 0:
        conversation = Conversation(msg.chat.id, msg.chat.first_name)
    else:
        conversation = Conversation(msg.chat.id, msg.chat.title)

    sender = User(msg['from'].id, msg['from'].first_name)
    if 'last_name' in msg['from']:
        sender.last_name = msg['from'].last_name
    if 'username' in msg['from']:
        sender.username = msg['from'].username

    # Gets the type of the message
    if 'text' in msg:
        type = 'text'
        content = msg.text
    else:
        type = None
        content = None

    date = msg.date

    if 'reply_to_message' in msg:
        reply = convert_message(msg.reply_to_message)
    else:
        reply = None

    extra = None

    return Message(id, conversation, sender, content, type, date, reply, extra)

def get_messages(bot):
    def get_updates(offset=None, limit=None, timeout=None):
        params = {}
        if offset:
            params['offset'] = offset
        if limit:
            params['limit'] = limit
        if timeout:
            params['timeout'] = timeout
        return api_request(bot, 'getUpdates', params)

    last_update = 0

    while (bot.started):
        res = get_updates(last_update + 1)
        if res:
            result = res.result
            for u in result:
                if u.update_id > last_update:
                    last_update = u.update_id

                    if 'inline_query' in u:
                        message = convert_inline(u.inline_query)
                        bot.inbox.put(message)

                    elif 'message' in u:
                        message = convert_message(u.message)
                        bot.inbox.put(message)

                    elif 'edited_message' in u:
                        message = convert_message(u.edited_message)
                        bot.inbox.put(message)

def send_message(bot, message):
    if message.type == 'text':
        api_request(bot, 'sendChatAction', params={"chat_id": message.conversation.id, "action": "typing"})
        params = {
            "chat_id": message.conversation.id,
            "text": message.content,
            "disable_web_page_preview": True,
        }
        if message.extra and 'format' in message.extra:
            params['parse_mode'] = message.extra['format']

        api_request(bot, 'sendMessage', params)

    elif message.type == 'photo':
        print('type photo')
        api_request(bot, 'sendChatAction', params={"chat_id": message.conversation.id, "action": "upload_photo"})
        params = {
            "chat_id": message.conversation.id,
            "photo": message.content,
        }

        if message.extra and 'caption' in message.extra:
            params['caption'] = message.extra['caption']

        files = None
        if not isinstance(photo, string_types):
            files = {'photo': photo}
        else:
            params['photo'] = photo
        print('api send photo')
        api_request(bot, 'sendPhoto', params, files = files)
    else:
        logging.debug("UNKNOWN MESSAGE TYPE")
