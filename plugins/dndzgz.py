from __main__ import *
from utilies import *

doc = config['command_start'] + 'zgzbus *[poste]*\nGets real time bus poste data. Only works for [Urbanos de Zaragoza](http://www.urbanosdezaragoza.es).'

triggers = {
	'^' + config['command_start'] + 'zgzbus',
	'^' + config['command_start'] + 'zgzbus',
	'^' + config['command_start'] + 'poste',
}

typing = True

def action(msg):
	input = get_input(msg.text)
		
	if not input:
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
		return core.send_message(msg.chat.id, locale['default']['errors']['connection'].format(jstr.status_code))
	
	jdat = json.loads(jstr.text)

	if jdat['items'] < 1:
		return core.send_message(msg.chat.id, locale['default']['errors']['results'])

	text = '*' + jdat['title'] + '*\n'
	for k,v in jdat['items']:
		text += '*' + first_word(k) + '* ' + get_input(k) + ' -> _' + get_input(v) + '_\n'
	
	core.send_message(msg.chat.id, text, parse_mode="Markdown")
