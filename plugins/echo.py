from __main__ import *
from utilies import *

doc = '/echo *[text]*\nRepeat a string.'
triggers = {
	'^/echo'
}

def action(msg):			
	input = get_input(msg.text)
		
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	core.send_message(msg.chat.id, input, parse_mode="Markdown")

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}