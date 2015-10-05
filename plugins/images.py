from __main__ import *
from utilies import *

doc = config.command_start + 'image *[query]*\nThis command performs a Google Images search for the given query. One random top result is returned. Safe search is enabled by default; use *' + config.command_start + 'insfw* to get potentially NSFW results.'

triggers = {
	'^' + config.command_start + 'images?',
	'^' + config.command_start + 'img',
	'^' + config.command_start + 'i ',
	'^' + config.command_start + 'insfw'
}

exts = {
	'.png$',
	'.jpg$',
	'.jpeg$',
	'.jpe$',
	'.gif$'
}

def action(msg):
	input = get_input(msg.text)
		
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
		
	url = 'http://ajax.googleapis.com/ajax/services/search/images'
	params = {
		'v': '1.0',
		'rsz': 8,
		'safe': 'active',
		'q': input
	}
	
	if msg.text.startswith(config.command_start + 'insfw'):
		del params['safe']
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	jdat = json.loads(jstr.text)

	if jdat['responseData']['results'] < 1:
		return core.send_message(msg.chat.id, config.locale.errors['results'])
		
	is_real = False
	counter = 0
	while is_real == False:
		counter = counter + 1
		if counter > 5 or len(jdat['responseData']['results']) < 1:
			return core.send_message(msg.chat.id, config.locale.errors['results'], parse_mode="Markdown")
		
		i = random.randint(1, len(jdat['responseData']['results']))-1

		result_url = jdat['responseData']['results'][i]['url']
		caption = '"' + input + '"'
		
		for v in exts:
			if re.compile(v).search(result_url):
				is_real = True
	
	download_and_send(msg.chat.id, result_url, 'photo', caption)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
}