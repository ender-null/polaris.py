from utilies import *

commands = [
	'^cat'
]
description = 'Get a cat pic!'
action = 'upload_photo'

def run(msg):			

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
		return send_error(msg, 'connection', jstr.status_code)
	
	photo = download(url)
	send_photo(msg['chat']['id'], photo)