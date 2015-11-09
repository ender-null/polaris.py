from __main__ import *
from utilies import *

commands = [
	'^konachan',
	'^k ',
	'^knsfw',
]
parameters = (
	('tags', True),
)
description = 'Gets an image from [Konachan](http://konachan.com); use *' + config['command_start'] + 'knsfw* to get potentially NSFW results.'
typing = True

def action(msg):
	input = get_input(msg.text)
	
	if not input:
		doc = get_doc(commands, parameters, description)
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	payload = input.replace(' ', '+')
	
	if not msg.text.startswith(config['command_start'] + 'knsfw'):
		payload += '+rating:s'
		
	url = 'http://konachan.com/post.json'
	url += '?limit=100&tags=' + payload
		
	jstr = requests.get(
		url
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	jdat = json.loads(jstr.text)
	
	if len(jdat) < 1:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['results'])
	
	i = random.randint(1, len(jdat))-1
	
	result_url = jdat[i]['file_url']
	caption = str(len(jdat)) + ' results matching: "' + input + '"'
	
	download_and_send(msg.chat.id, result_url, 'photo', caption)