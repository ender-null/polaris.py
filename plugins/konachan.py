from __main__ import *
from utilies import *

doc = config.command_start + 'konachan *[tags]*\nGets an image from [Konachan](http://konachan.com); use *' + config.command_start + 'knsfw* to get potentially NSFW results.'

triggers = {
	'^' + config.command_start + 'konachan',
	'^' + config.command_start + 'k ',
	'^' + config.command_start + 'knsfw'
}

def action(msg):
	input = get_input(msg.text)
	
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	payload = input.replace(' ', '+')
	
	if not msg.text.startswith(config.command_start + 'knsfw'):
		payload += '+rating:s'
		
	url = 'http://konachan.com/post.json'
	url += '?limit=100&tags=' + payload
		
	jstr = requests.get(
		url
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	jdat = json.loads(jstr.text)
	
	if len(jdat) < 1:
		return core.send_message(msg.chat.id, config.locale.errors['results'])
	
	i = random.randint(1, len(jdat))-1
	
	result_url = jdat[i]['file_url']
	caption = str(len(jdat)) + ' results matching: "' + input + '"'
	
	download_and_send(msg.chat.id, result_url, 'photo', caption)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
}