from __main__ import *
from utilies import *

doc = '/images *[query]*\nThis command performs a Google Images search for the given query. One random top result is returned. Safe search is enabled by default; use */insfw* to get potentially NSFW results.'

triggers = {
	'^/images?',
	'^/img',
	'^/i ',
	'^/insfw'
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
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'] + '\nError: ' + str(jstr.status_code))
	
	jdat = json.loads(jstr.text)

	if jdat['responseData']['results'] < 1:
		return core.send_message(msg.chat.id, config.locale.errors['results'])
		
	is_real = False
	counter = 0
	while is_real == False:
		counter = counter + 1
		if counter > 5 or len(jdat['responseData']['results']) < 1:
			return core.send_message(msg.chat.id, config.locale.errors['results'])
		
		i = random.randint(1, len(jdat['responseData']['results']))-1

		result_url = jdat['responseData']['results'][i]['url']
		caption = jdat['responseData']['results'][i]['titleNoFormatting']
		
		for v in exts:
			if re.compile(v).search(result_url):
				is_real = True
	
	download_and_send(msg.chat.id, result_url, 'photo', caption)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
}