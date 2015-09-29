from __main__ import *
from utilies import *

doc = '/voice *[text]*\nSays something... in the cool way.'
triggers = {
	'^/voice',
	'^/say',
	'^/di',
}

def action(msg):			
	input = get_input(msg.text)
	
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	if re.compile('di').search(msg.text):
		lang = 'es'
	else:
		lang = 'en'
	
	url = 'http://translate.google.com/translate_tts'
	params = {
		'tl': lang,
		'q': input,
		'client': 't'
	}
	headers = {
		"Referer": 'http://translate.google.com/',
		"User-Agent": "stagefright/1.2 (Linux;Android 5.0)"
	}
	
	jstr = requests.get(
		url,
		params = params,
		headers = headers
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'] + '\nError: ' + str(jstr.status_code))
	
	result_url = jstr.url
	
	download_and_send(msg.chat.id, url, 'voice', headers=headers, params=params)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
}