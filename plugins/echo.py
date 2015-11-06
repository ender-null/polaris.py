from __main__ import *
from utilies import *

commands = [
	'^echo'
]
parameters = (
	('text', True),
)
description = 'Repeat a string.'
typing = True

def action(msg):
	input = get_input(msg.text)
		
	if not input:
		doc = commands[0].replace('^', config['command_start']) + '\n' + description
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")

	core.send_message(msg.chat.id, input, parse_mode="Markdown")