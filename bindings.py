import requests
import json
from six import string_types

def get_token():
	return json.load(open('data/config.json'))['api']['telegram_bot']

api_url = 'https://api.telegram.org/bot' + get_token() + '/'

def send_request(url, params=None, headers=None, files=None):
	jstr = requests.post(
		url,
		params = params,
		headers = headers,
		files = files
	)
	
	if jstr.status_code != 200:
		return False
	
	return json.loads(jstr.text)

def api_request(api_method, params=None, headers=None, files=None):
	url = api_url + api_method
	
	return send_request(url, params, headers, files)
	
def get_me():
	return api_request('getMe')

def send_message(chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None, parse_mode=None):
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
	
def forward_message(chat_id, from_chat_id, message_id):
	params = {
		'chat_id': chat_id,
		'from_chat_id': from_chat_id,
		'message_id': message_id
	}
	return api_request('forwardMessage', params)
	
def send_photo(chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None):
	params = {
		'chat_id': chat_id
	}
	
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

def send_audio(chat_id, audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None):
	params = {
		'chat_id': chat_id
	}
	
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
	if reply_markup:
		params['reply_markup'] = reply_markup
	
	return api_request('sendAudio', params, files=files)

def send_document(chat_id, document, reply_to_message_id=None, reply_markup=None):
	params = {
		'chat_id': chat_id
	}
	
	files = None
	if not isinstance(document, string_types):
		files = {'document': document}
	else:
		params['document'] = document
	if reply_to_message_id:
		params['reply_to_message_id'] = reply_to_message_id
	if reply_markup:
		params['reply_markup'] = reply_markup
	
	return api_request('sendDocument', params, files=files)

def send_sticker(chat_id, sticker, reply_to_message_id=None, reply_markup=None):
	params = {
		'chat_id': chat_id
	}
	
	files = None
	if not isinstance(sticker, string_types):
		files = {'sticker': sticker}
	else:
		params['sticker'] = sticker
	if reply_to_message_id:
		params['reply_to_message_id'] = reply_to_message_id
	if reply_markup:
		params['reply_markup'] = reply_markup
	
	return api_request('sendSticker', params, files=files)
	
def send_video(chat_id, video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None):
	params = {
		'chat_id': chat_id
	}
	
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
	if reply_markup:
		params['reply_markup'] = reply_markup
	
	return api_request('sendVideo', params, files=files)
	
def send_voice(chat_id, voice, duration=None, reply_to_message_id=None, reply_markup=None):
	params = {
		'chat_id': chat_id
	}
	
	files = None
	if not isinstance(voice, string_types):
		files = {'voice': voice}
	else:
		params['voice'] = voice
	if duration:
		params['duration'] = duration
	if reply_to_message_id:
		params['reply_to_message_id'] = reply_to_message_id
	if reply_markup:
		params['reply_markup'] = reply_markup
	
	return api_request('sendVoice', params, files=files)
	
def send_location(chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None):
	params = {
		'chat_id': chat_id,
		'longitude': latitude,
		'longitude': longitude
	}
	
	if reply_to_message_id:
		params['reply_to_message_id'] = reply_to_message_id
	if reply_markup:
		params['reply_markup'] = reply_markup
	
	return api_request('sendLocation', params, files=files)
	
def send_chat_action(chat_id, action):
	params = {
		'chat_id': chat_id,
		'action': action
	}
	return api_request('sendChatAction', params)
	
def get_user_profile_photos(user_id, offset=None, limit=None):
	params = {
		'user_id': user_id
	}
	
	if offset:
		params['offset'] = offset
	if limit:
		params['limit'] = limit
		
	return api_request('getUserProfilePhotos', params)
	
def get_updates(offset=None, limit=None, timeout=None):
	params = {}
	if offset:
		params['offset'] = offset
	if limit:
		params['limit'] = limit
	if timeout:
		params['timeout'] = timeout
	return api_request('getUpdates', params)
	
def set_webhook(url=None, certificate=None):
	params = {}
	if url:
		params['url'] = url
	if certificate:
		params['certificate'] = certificate
	return api_request('setWebhook', params)
	
def get_file(file_id):
	params = {
		'file_id': file_id
	}
	return api_request('getFile', params)
	