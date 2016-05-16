from core.shared import *
from six import string_types
from time import time
import requests

# Telegram Bot API methods
api_url = 'https://api.telegram.org/bot' + config.keys.bot_api_token + '/'


def send_request(url, params=None, headers=None, files=None, data=None):
    result = requests.get(url, params=params, headers=headers, files=files, data=data)
    if result.status_code != 200:
        print(result.text)

        while result.status_code == 429:
            result = requests.get(url, params=params, headers=headers, files=files, data=data)

    return json.loads(result.text)


def api_request(api_method, params=None, headers=None, files=None):
    url = api_url + api_method

    return DictObject(send_request(url, params, headers, files))


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
                     reply_to_message_id=None, parse_mode=None, disable_notification=False, reply_markup=None):
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

    return api_request('sendMessage', params)


def api_forward_message(chat_id, from_chat_id, message_id):
    params = {
        'chat_id': chat_id,
        'from_chat_id': from_chat_id,
        'message_id': message_id
    }

    return api_request('forwardMessage', params)


def api_send_photo(chat_id, photo, caption=None,
                   reply_to_message_id=None, disable_notification=False, reply_markup=None):
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
        params['reply_markup'] = json.dumps(reply_markup)
    if disable_notification:
        params['disable_notification'] = disable_notification

    return api_request('sendPhoto', params, files=files)


def api_send_audio(chat_id, audio, title=None, duration=None, performer=None,
                   reply_to_message_id=None, disable_notification=False, reply_markup=None):
    params = {'chat_id': chat_id}

    files = None
    if not isinstance(audio, string_types):
        files = {'audio': audio}
    else:
        params['audio'] = audio
    if duration:
        params['duration'] = duration
    if performer:
        params['performer'] = performer
    if title:
        params['title'] = title
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if disable_notification:
        params['disable_notification'] = disable_notification
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)

    return api_request('sendAudio', params, files=files)


def api_send_document(chat_id, document, caption=None, reply_to_message_id=None, disable_notification=False, reply_markup=None):
    params = {'chat_id': chat_id}

    files = None
    if not isinstance(document, string_types):
        files = {'document': document}
    else:
        params['document'] = document
    if caption:
        params['caption'] = caption
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if disable_notification:
        params['disable_notification'] = disable_notification
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)

    return api_request('sendDocument', params, files=files)


def api_send_sticker(chat_id, sticker, reply_to_message_id=None, disable_notification=False, reply_markup=None):
    params = {'chat_id': chat_id}

    files = None
    if not isinstance(sticker, string_types):
        files = {'sticker': sticker}
    else:
        params['sticker'] = sticker
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if disable_notification:
        params['disable_notification'] = disable_notification
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)

    return api_request('sendSticker', params, files=files)


def api_send_video(chat_id, video, caption=None, duration=None,
                   reply_to_message_id=None, disable_notification=False, reply_markup=None):
    params = {'chat_id': chat_id}

    files = None
    if not isinstance(video, string_types):
        files = {'video': video}
    else:
        params['video'] = video
    if duration:
        params['duration'] = duration
    if caption:
        params['caption'] = caption
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if disable_notification:
        params['disable_notification'] = disable_notification
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)

    return api_request('sendVideo', params, files=files)


def api_send_voice(chat_id, voice, duration=None, reply_to_message_id=None, disable_notification=False, reply_markup=None):
    params = {'chat_id': chat_id}

    files = None
    if not isinstance(voice, string_types):
        files = {'voice': voice}
    else:
        params['voice'] = voice
    if duration:
        params['duration'] = duration
    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if disable_notification:
        params['disable_notification'] = disable_notification
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)

    return api_request('sendVoice', params, files=files)


def api_send_location(chat_id, latitude, longitude, reply_to_message_id=None, disable_notification=False, reply_markup=None):
    params = {
        'chat_id': chat_id,
        'latitude': latitude,
        'longitude': longitude
    }

    if reply_to_message_id:
        params['reply_to_message_id'] = reply_to_message_id
    if disable_notification:
        params['disable_notification'] = disable_notification
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)

    return api_request('sendLocation', params)


def api_send_chat_action(chat_id, action):
    params = {
        'chat_id': chat_id,
        'action': action
    }
    return api_request('sendChatAction', params)

def api_forward_message(chat_id, from_chat_id, message_id, disable_notification=False):
    params = {
        'chat_id': chat_id,
        'from_chat_id': from_chat_id,
        'message_id': message_id
    }

    if disable_notification:
            params['disable_notification'] = disable_notification

    return api_request('forwardMessage', params)


def api_answer_inline_query(inline_query_id, results, cache_time=None, is_personal=None, next_offset=None):
    params = {
        'inline_query_id': inline_query_id,
        'results': json.dumps(results)
    }
    if cache_time:
        params['cache_time'] = cache_time
    if is_personal:
        params['is_personal'] = is_personal
    if next_offset:
        params['url'] = next_offset

    return api_request('answerInlineQuery', params)


def convert_inline(qry):
    id = qry['id']
    sender = User()
    sender.id = qry['from']['id']
    sender.first_name = qry['from']['first_name']
    if 'last_name' in qry['from']:
        sender.last_name = qry['from']['last_name']
    if 'username' in qry['from']:
        sender.username = qry['from']['username']

    type = 'inline_query'
    content = qry['query']
    extra = qry['offset']
    date = time()

    return Message(id, sender, bot, content, type, date, extra=extra)


# Standard methods for bindings
def get_me():
    result = api_request('getMe')
    bot.first_name = result['result']['first_name']
    bot.username = result['result']['username']
    bot.id = result['result']['id']
    
    
def kick_chat_member(chat_id, user_id):
    params = {
        'chat_id': chat_id,
        'user_id': user_id
    }
    
    result = api_request('kickChatMember', params)
    
    if result.ok == False:
        if result.description.split(': ')[1] == 'CHAT_ADMIN_REQUIRED' or result.description.split(': ')[1] == 'Not enough rights to kick participant':
            raise PolarisExceptions.NotAdminException()
        else:
            raise PolarisExceptions.FailedException()
            
    else:
        return True
    
def unban_chat_member(chat_id, user_id):
    params = {
        'chat_id': chat_id,
        'user_id': user_id
    }
    
    result = api_request('unbanChatMember', params)
    
    if result.ok == False:
        if result.description.split(': ')[1] == 'CHAT_ADMIN_REQUIRED' or result.description.split(': ')[1] == 'Not enough rights to kick participant':
            raise PolarisExceptions.NotAdminException()
        else:
            raise PolarisExceptions.FailedException()
            
    else:
        return True

def convert_message(msg):
    id = msg['message_id']
    if msg['chat']['id'] > 0:
        receiver = User()
        receiver.first_name = msg['chat']['first_name']
        if 'last_name' in msg['chat']:
            receiver.last_name = msg['chat']['last_name']
        if 'username' in msg['chat']:
            receiver.username = msg['chat']['username']
    else:
        receiver = Group()
        receiver.title = msg['chat']['title']
    receiver.id = msg['chat']['id']
    sender = User()
    sender.id = msg['from']['id']
    sender.first_name = msg['from']['first_name']
    if 'last_name' in msg['from']:
        sender.last_name = msg['from']['last_name']
    if 'username' in msg['from']:
        sender.username = msg['from']['username']
    date = msg['date']

    # Gets the type of the message
    if 'text' in msg:
        type = 'text'
        content = msg['text']
        extra = None
        
        if 'entities' in msg:
            for entity in msg['entities']:
                if entity['type'] == 'url':
                    type = 'url'
                    content = msg['text'][entity['offset']:entity['offset']+entity['length']]
                    extra = None

    elif 'audio' in msg:
        type = 'audio'
        content = msg['audio']['file_id']
        if 'title' in msg['audio']:
            extra = msg['audio']['title']
        else:
            extra = None
    elif 'document' in msg:
        type = 'document'
        content = msg['document']['file_id']
        if 'file_name' in msg:
            extra = msg['document']['file_name']
        else:
            extra = None
    elif 'photo' in msg:
        type = 'photo'
        content = msg['photo'][-1]['file_id']
        if 'caption' in msg:
            extra = msg['caption']
        else:
            extra = None
    elif 'sticker' in msg:
        type = 'sticker'
        content = msg['sticker']['file_id']
        extra = None
    elif 'video' in msg:
        type = 'video'
        content = msg['video']['file_id']
        if 'caption' in msg:
            extra = msg['caption']
        else:
            extra = None
    elif 'voice' in msg:
        type = 'voice'
        content = msg['voice']['file_id']
        extra = None
    elif 'contact' in msg:
        type = 'contact'
        content = msg['contact']['phone_number']
        extra = msg['contact']['first_name']
    elif 'location' in msg:
        type = 'location'
        content = msg['location']['latitude']
        extra = msg['location']['longitude']
    elif 'new_chat_member' in msg:
        type = 'service'
        content = 'join_user'
        extra = User()
        extra.first_name = msg['new_chat_member']['first_name']
        if 'last_name' in msg['new_chat_member']:
            extra.last_name = msg['new_chat_member']['last_name']
        if 'username' in msg['new_chat_member']:
            extra.username = msg['new_chat_member']['username']
    elif 'left_chat_member' in msg:
        type = 'service'
        content = 'left_user'
        extra = User()
        extra.first_name = msg['left_chat_member']['first_name']
        if 'last_name' in msg['left_chat_member']:
            extra.last_name = msg['left_chat_member']['last_name']
        if 'username' in msg['left_chat_member']:
            extra.username = msg['left_chat_member']['username']
    elif ('new_chat_title' in msg
          or 'new_chat_photo' in msg
          or 'delete_chat_photo' in msg
          or 'group_chat_created' in msg
          or 'supergroup_chat_created' in msg
          or 'channel_chat_created' in msg
          or 'migrate_to_chat_id'
          or 'migrate_from_chat_id' in msg):
        type = 'service'
        content = None
        extra = None
    else:
        type = None
        content = None
        extra = None

    if 'reply_to_message' in msg:
        reply = convert_message(msg['reply_to_message'])
    else:
        reply = None

    return Message(id, sender, receiver, content, type, date, reply, extra)


def send_message(message):
    if message.type == 'text':
        api_send_chat_action(message.receiver.id, 'typing')
        api_send_message(message.receiver.id, message.content, not message.extra, parse_mode=message.markup, reply_markup=message.keyboard, disable_notification=message.silent)
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
        print('UNKNOWN MESSAGE TYPE: ' + message.type)


def inbox_listener():
    last_update = 0

    while (True):
        updates = get_updates(last_update + 1)
        result = updates['result']

        if result:
            for update in result:
                if update['update_id'] > last_update:
                    last_update = update['update_id']

                    if 'inline_query' in update:
                        message = convert_inline(update['inline_query'])
                        inbox.put(message)

                    elif 'message' in update:
                        message = convert_message(update['message'])
                        inbox.put(message)
