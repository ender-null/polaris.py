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
		return 'Connection error: ' + jstr.status_code
	
	return json.loads(jstr.text)

def api_request(api_method, params=None, headers=None, files=None):
	url = api_url + api_method
	
	return send_request(url, params, headers, files)
	
def get_me():
	return api_request('getMe')
	
def get_updates(offset=None):
	params = {}
	if offset:
		params['offset'] = offset
	return api_request('getUpdates', params)

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
	
def forward_message(chat_id, from_chat_id, message_id):
	params = {
		'chat_id': chat_id,
		'from_chat_id': from_chat_id,
		'message_id': message_id
	}
	return api_request('sendMessage', params)
	
def send_chat_action(chat_id, action):
	params = {
		'chat_id': chat_id,
		'action': action
	}
	return api_request('sendChatAction', params)