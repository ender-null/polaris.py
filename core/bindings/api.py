from core.shared import *
from threading import Thread
from six import string_types
import requests

# Telegram Bot API methods
api_url = 'https://api.telegram.org/bot' + config.keys.bot_api_token + '/'


def send_request(url, params=None, headers=None, files=None, data=None):
    result = requests.get(url, params=params, headers=headers, files=files, data=data)

    if result.status_code != 200:
        print(result.text)
        return False

    return json.loads(result.text)


def api_request(api_method, params=None, headers=None, files=None):
    url = api_url + api_method

    return send_request(url, params, headers, files)


def get_updates(offset=None, limit=None, timeout=None):
    params = {}
    if offset:
        params['offset'] = offset
    if limit:
        params['limit'] = limit
    if timeout:
        params['timeout'] = timeout
    return api_request('getUpdates', params)


def api_send_message(chat_id, text, disable_web_page_preview=None,
                     reply_to_message_id=None, reply_markup=None, parse_mode=None):
    params = {
        'chat_id': chat_id,
        'text': text,
    }

    if disable_web_page_preview:
        params['disable_web_page_preview'] = disable_web_page_preview
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if reply_markup:
        params['reply_markup'] = reply_markup
    if parse_mode:
        params['parse_mode'] = parse_mode

    return api_request('sendMessage', params)


def api_forward_message(chat_id, from_chat_id, message_id):
    params = {
        'chat_id': chat_id,
        'from_chat_id': from_chat_id,
        'message_id': message_id
    }

    return api_request('forwardMessage', params)


def api_send_photo(chat_id, photo, caption=None,
                   reply_to_message_id=None, reply_markup=None):
    params = {'chat_id': chat_id}

    files = None
    if not isinstance(photo, string_types):
        files = {'photo': photo}
    else:
        params['photo'] = photo
    if caption:
        params['caption'] = caption
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if reply_markup:
        params['reply_markup'] = reply_markup

    return api_request('sendPhoto', params, files=files)


# Standard methods for bindings
def get_me():
    result = api_request('getMe')
    bot.first_name = result['result']['first_name']
    bot.username = result['result']['username']
    bot.id = result['result']['id']


def convert_message(msg):
    id = msg['message_id']
    if msg['chat']['id'] > 0:
        receiver = User
        receiver.first_name = msg['chat']['first_name']
        if 'last_name' in msg['from']:
            receiver.last_name = msg['chat']['last_name']
        receiver.username = msg['chat']['username']
    else:
        receiver = Group
        receiver.title = msg['chat']['title']
    receiver.id = msg['chat']['id']
    sender = User
    sender.id = msg['from']['id']
    sender.first_name = msg['from']['first_name']
    if 'last_name' in msg['from']:
        sender.last_name = msg['from']['last_name']
    if 'username' in msg['from']:
        sender.username = msg['from']['username']
    content = msg['text']
    date = msg['date']

    # Gets the type of the message
    if 'text' in msg:
        type = 'text'
    elif 'audio' in msg:
        type = 'audio'
    elif 'document' in msg:
        type = 'document'
    elif 'photo' in msg:
        type = 'photo'
    elif 'sticker' in msg:
        type = 'sticker'
    elif 'video' in msg:
        type = 'video'
    elif 'voice' in msg:
        type = 'voice'
    elif 'contact' in msg:
        type = 'contact'
    elif 'location' in msg:
        type = 'location'
    elif ('new_chat_participant' in msg
          or 'left_chat_participant' in msg
          or 'new_chat_title' in msg
          or 'new_chat_photo' in msg
          or 'delete_chat_photo' in msg
          or 'group_chat_created' in msg
          or 'supergroup_chat_created' in msg
          or 'channel_chat_created' in msg
          or 'migrate_to_chat_id'
          or 'migrate_from_chat_id' in msg):
        type = 'status'
    else:
        type = None

    if 'reply_to_message' in msg:
        reply = convert_message(msg['reply_to_message'])
    else:
        reply = None

    return Message(id, sender, receiver, content, type, date, reply)


def send_message(message):
    if message.type == 'text':
        api_send_message(message.receiver.id, message.content, message.extra, parse_mode=message.markup)
    elif message.type == 'photo':
        api_send_photo(message.receiver.id, message.content, message.extra)


def inbox_listen():
    print('\tStarting inbox daemon...')
    last_update = 0

    while (started):
        updates = get_updates(last_update + 1)
        result = updates['result']

        if result:
            for update in result:
                if update['update_id'] > last_update:
                    last_update = update['update_id']
                    msg = update['message']

                    if (not 'inline_query' in update and 'text' in msg):
                        # Generates another message object for the original message if the reply.
                        message = convert_message(msg)
                        inbox.put(message)


def outbox_listen():
    while (started):
        message = outbox.get()
        if message.type == 'text':
            if message.receiver.id > 0:
                print('\nOUTBOX: [{0}] {1}'.format(message.receiver.first_name, message.content))
            else:
                print('\nOUTBOX: [{0}] {1}'.format(message.receiver.title, message.content))
        else:
            if message.receiver.id > 0:
                print('\nOUTBOX: [{0}] <{1}>'.format(message.receiver.first_name, message.type))
            else:
                print('\nOUTBOX: [{0}] <{1}>'.format(message.receiver.title, message.type))
        send_message(message)


def init():
    print('\nInitializing Telegram Bot API...')
    get_me()
    print('\tUsing: {0} (@{1})'.format(bot.first_name, bot.username))

    Thread(target=inbox_listen, name='Inbox Listener').start()
    Thread(target=outbox_listen, name='Outbox Listener').start()

