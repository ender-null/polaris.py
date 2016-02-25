from core.shared import *
from threading import Thread
from six import string_types
import requests

# Telegram Bot API methods
api_url = 'https://api.telegram.org/bot' + config.keys.bot_api_token + '/'


def send_request(url, params=None, headers=None, files=None, data=None):
    # print('\tRequest: ' + url)

    result = requests.get(url, params=params, headers=headers, files=files, data=data)

    if result.status_code != 200:
        print('NOT OK')
        print(result.text)
        return False

    # print(result.text)

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


def send_message(message):
    if message.type == 'text':
        api_send_message(message.receiver.id, message.content, message.extra, parse_mode=message.markup)
    elif message.type == 'photo':
        api_send_photo(message.receiver.id, message.content, message.extra)

def inbox_listen():
    print('\tStarting inbox daemon...')
    last_update = 0

    while (True):
        updates = get_updates(last_update + 1)
        result = updates['result']

        if result:
            for update in result:
                if update['update_id'] > last_update:
                    last_update = update['update_id']
                    msg = update['message']

                    if (not 'inline_query' in update and 'text' in msg):
                        # Generates a Message object and sends it to the inbox queue.
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

                        # Generates another message object for the original message if the reply.
                        if 'reply_to_message' in msg:
                            reply_id = msg['message_id']
                            if msg['reply_to_message']['chat']['id'] > 0:
                                reply_receiver = User
                                reply_receiver.first_name = msg['reply_to_message']['chat']['first_name']
                                if 'last_name' in msg['reply_to_message']['from']:
                                    reply_receiver.last_name = msg['reply_to_message']['chat']['last_name']
                                reply_receiver.username = msg['reply_to_message']['chat']['username']
                            else:
                                reply_receiver = Group
                                reply_receiver.title = msg['reply_to_message']['chat']['title']
                            reply_receiver.id = msg['reply_to_message']['chat']['id']
                            reply_sender = User
                            reply_sender.id = msg['reply_to_message']['from']['id']
                            reply_sender.first_name = msg['reply_to_message']['from']['first_name']
                            if 'last_name' in msg['reply_to_message']['from']:
                                reply_sender.last_name = msg['reply_to_message']['from']['last_name']
                            reply_sender.username = msg['reply_to_message']['from']['username']
                            reply_content = msg['reply_to_message']['text']
                            reply_date = msg['reply_to_message']['date']

                            # Gets the type of the message
                            if 'text' in msg['reply_to_message']:
                                reply_type = 'text'
                            elif 'audio' in msg['reply_to_message']:
                                reply_type = 'audio'
                            elif 'document' in msg['reply_to_message']:
                                reply_type = 'document'
                            elif 'photo' in msg['reply_to_message']:
                                reply_type = 'photo'
                            elif 'sticker' in msg['reply_to_message']:
                                reply_type = 'sticker'
                            elif 'video' in msg['reply_to_message']:
                                reply_type = 'video'
                            elif 'voice' in msg['reply_to_message']:
                                reply_type = 'voice'
                            elif 'contact' in msg['reply_to_message']:
                                reply_type = 'contact'
                            elif 'location' in msg['reply_to_message']:
                                reply_type = 'location'
                            elif ('new_chat_participant' in msg['reply_to_message']
                                  or 'left_chat_participant' in msg['reply_to_message']
                                  or 'new_chat_title' in msg['reply_to_message']
                                  or 'new_chat_photo' in msg['reply_to_message']
                                  or 'delete_chat_photo' in msg['reply_to_message']
                                  or 'group_chat_created' in msg['reply_to_message']
                                  or 'supergroup_chat_created' in msg['reply_to_message']
                                  or 'channel_chat_created' in msg['reply_to_message']
                                  or 'migrate_to_chat_id'
                                  or 'migrate_from_chat_id' in msg['reply_to_message']):
                                reply_type = 'status'
                            else:
                                reply_type = None

                            reply = Message(reply_id, reply_sender, reply_receiver, reply_content, reply_type,
                                            reply_date)
                        else:
                            reply = None

                        message = Message(id, sender, receiver, content, type, date, reply)
                        inbox.put(message)


def outbox_listen():
    while (True):
        message = outbox.get()
        if message.type == 'text':
            print('OUTBOX: ' + message.content)
        else:
            print('OUTBOX: [{0}]'.format(message.type))
        send_message(message)


inbox_listener = Thread(target=inbox_listen, name='Inbox Listener')
outbox_listener = Thread(target=outbox_listen, name='Outbox Listener')


def init():
    print('\nInitializing Telegram Bot API...')
    get_me()
    print('\tUsing: {0} (@{1})'.format(bot.first_name, bot.username))

    inbox_listener.start()
    outbox_listener.start()

