from __main__ import *
from utilies import *

commands = [
	'^bus',
	'^poste',
	'^zgzbus',
]
parameters = (
	('poste', True),
)
description = 'Gets real time bus poste data. Only works for [Urbanos de Zaragoza](http://www.urbanosdezaragoza.es).'
typing = True

def action(msg):
	input = get_input(msg.text)
		
	if not input:
		doc = get_doc(commands, parameters, description)
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
		
	url = 'http://www.dndzgz.com/point'
	params = {
		'service': 'bus',
		'id': input
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(jstr.status_code))
	
	jdat = json.loads(jstr.text)
		
	if 'Error obteniendo datos' in jdat['items'][0]:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['results'])

	text = '*' + jdat['title'] + '*\n'
	for k,v in jdat['items']:
		text += '*' + first_word(k) + '* ' + get_input(k) + ' -> _' + get_input(v) + '_\n'
	
	core.send_message(msg.chat.id, text, parse_mode="Markdown")
