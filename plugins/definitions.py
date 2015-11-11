from __main__ import *
from utilies import *

commands = [
	'^define',
	'^ud',
	'^urbandictionary'
]
parameters = (
	('term', True),
)
description = 'Returns the first definition for a given term from [Urban Dictionary](http://urbandictionary.com).'
typing = True

def action(msg):
	input = get_input(msg['text'])
		
	if not input:
		doc = get_doc(commands, parameters, description)
		return send_message(msg['chat']['id'], doc, parse_mode="Markdown")
		
	url = 'http://api.urbandictionary.com/v0/define'
	params = {
		'term': input
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return send_error(msg, 'connection', jstr.status_code)
	
	jdat = json.loads(jstr.text)

	if jdat['result_type'] == 'no_results':
		return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['results'])

	i = random.randint(1, len(jdat['list']))-1
	
	text = '*' + jdat['list'][i]['word'] + '*\n'
	text += jdat['list'][i]['definition'] + '\n'
	if jdat['list'][i]['example']:
		text += '\nExample:\n_' + jdat['list'][i]['example'] + '_'
	
	send_message(msg['chat']['id'], text, parse_mode="Markdown")
