from __main__ import *
from utilies import *

doc = '/cat\nGet a cat pic!'
triggers = {
	'^/cats?'
}

def action(msg):			

	url = 'http://thecatapi.com/api/images/get'
	params = {
		'format': 'src',
		'api_key': config.apis['catapi']
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(jstr.status_code))
	
	download_and_send(msg.chat.id, url, 'photo')

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
}