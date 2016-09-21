from polaris.types import Message, User
from polaris.utils import send_request
from six import string_types
from time import time
import requests, logging

# Telegram Bot API methods
api_url = 'https://api.telegram.org/bot'

def api_request(bot, api_method, params=None, headers=None, files=None):
    url = api_url + bot.config.connector_token + '/' + api_method

    try:
        return send_request(url, params, headers, files)
    except:
        return None

def api_send_message(chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, parse_mode=None, disable_notification=False, reply_markup=None, bot=None):
    params = {
        'chat_id': chat_id,
        'text': text,
    }

    if disable_web_page_preview:
        params['disable_web_page_preview'] = disable_web_page_preview
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)
    if parse_mode:
        params['parse_mode'] = parse_mode
    if disable_notification:
        params['disable_notification'] = disable_notification
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)

    return api_request(bot, 'sendMessage', params)

def api_send_chat_action(chat_id, action, bot=None):
    params = {
        'chat_id': chat_id,
        'action': action
    }
    return api_request(bot, 'sendChatAction', params)


# Connector methods for Polaris
def get_me(bot):
    r = api_request(bot, 'getMe')
    return User(r.result.id, r.result.first_name, r.result.last_name, r.result.username)


def convert_message(msg):
    id = msg.message_id
    if msg.chat.id > 0:
        conversation = Message.Conversation(msg.chat.id, msg.chat.first_name)
    else:
        conversation = Message.Conversation(msg.chat.id, msg.chat.title)

    sender = User(msg._from_.id, msg._from_.first_name)
    if 'last_name' in msg._from_:
        sender.last_name = msg._from_.last_name
    if 'username' in msg._from_:
        sender.username = msg._from_.username

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
        api_send_chat_action(message.conversation.id, 'typing', bot=bot)
        api_send_message(message.conversation.id, message.content, True, parse_mode=message.markup, bot=bot)
    elif message.type == 'photo':
        api_send_chat_action(message.receiver.id, 'upload_photo')
        api_send_photo(message.receiver.id, message.content, message.extra, reply_markup=message.keyboard, disable_notification=message.silent)
    elif message.type == 'audio':
        api_send_chat_action(message.receiver.id, 'upload_audio')
        api_send_audio(message.receiver.id, message.content, message.extra, reply_markup=message.keyboard, disable_notification=message.silent)
    elif message.type == 'document':
        api_send_chat_action(message.receiver.id, 'upload_document')
        api_send_document(message.receiver.id, message.content, message.extra, reply_markup=message.keyboard, disable_notification=message.silent)
    elif message.type == 'sticker':
        api_send_sticker(message.receiver.id, message.content, message.extra, reply_markup=message.keyboard, disable_notification=message.silent)
    elif message.type == 'video':
        api_send_chat_action(message.receiver.id, 'upload_video')
        api_send_video(message.receiver.id, message.content, message.extra, reply_markup=message.keyboard, disable_notification=message.silent)
    elif message.type == 'voice':
        api_send_chat_action(message.receiver.id, 'record_audio')
        api_send_voice(message.receiver.id, message.content, message.extra, reply_markup=message.keyboard, disable_notification=message.silent)
    elif message.type == 'location':
        api_send_chat_action(message.receiver.id, 'find_location')
        api_send_location(message.receiver.id, message.content, message.extra, reply_markup=message.keyboard, disable_notification=message.silent)
    elif message.type == 'inline_results':
        api_answer_inline_query(message.id, message.content, next_offset=message.extra)
    elif message.type == 'forward':
        api_forward_message(message.content, message.receiver.id, message.id)
    elif message.type == 'service':
        api_send_message(message.receiver.id, '`Not Yet Implemented!`', parse_mode='Markdown')
    else:
        logging.error('UNKNOWN MESSAGE TYPE: ' + message.type)
