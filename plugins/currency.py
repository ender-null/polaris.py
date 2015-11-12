from __main__ import *
from utilies import *

commands = [
	'^currency',
	'^cash',
	'^c '
]
parameters = (
	('to', True),
	('from', True),
	('amount', False),
)
description = 'Convert an amount from one currency to another.'
action = 'typing'
hidden = True

def run(msg):
	input = get_input(msg['text'])

	if not input:
		doc = get_doc(commands, parameters, description)
		return send_message(msg['chat']['id'], doc, parse_mode="Markdown")	
	
	print input
	from_currency = first_word(input).upper()
	print from_currency
	to = first_word(input, 2).upper()
	print to
	amount = first_word(input, 3)
	print amount

	if not int(amount):
		amount = 1
		result = 1

	if from_currency != to:
		url = 'http://www.google.com/finance/converter'
		params = {
			'from': from_currency,
			'to': to,
			'a': amount
		}
		
		jstr = requests.get(
			url,
			params = params,
		)
			
		if jstr.status_code != 200:
			return send_error(msg, 'connection', jstr.status_code)

		
		print jstr.url
		
		str = re.match("<span class=bld>(.*) %u+</span>", jstr.text).group(1)
		if not str:
			return send_error(msg, 'results')
		result = str

	message = amount + ' ' + from_currency + ' = ' + result + ' ' + to
	
	send_message(msg['chat']['id'], lat, lon)