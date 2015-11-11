from utilies import *

commands = [
	'^cat'
]
description = 'Get a cat pic!'
typing = True

def action(msg):			

	url = 'http://thecatapi.com/api/images/get'
	params = {
		'format': 'src',
		'api_key': config['api']['catapi']
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(jstr.status_code))
	
	photo = download(url)
	send_photo(msg.chat.id, photo)