from __main__ import *
from utilies import *

doc = '/help _[command]_\nGet list of basic information for all commands, or more detailed documentation on a specified command.'
triggers = {
	'^/help',
	'^/h$',
}

def action(msg):			
	input = get_input(msg.text)
	
	if input:
		for i,v in plugins.items():
			if hasattr(v, 'doc'):
				if '/' + input == v.doc.splitlines()[0]:
					return core.send_message(msg.chat.id, v.doc, parse_mode="Markdown")
		
	help = ''
	for i,v in plugins.items():
		if hasattr(v, 'doc'):
			a = v.doc.splitlines()[0]
			help += a + '\n'
		
	message = '*Commands*:\n' + help
	
	if msg.from_user.id != msg.chat.id:
		if not core.send_message(msg.from_user.id, message, parse_mode="Markdown"):
			return core.send_message(msg.chat.id, message, parse_mode="Markdown")
		return core.send_message(msg.chat.id, 'I have sent you the requested information in a *private message*.', parse_mode="Markdown")
	else:
		return core.send_message(msg.chat.id, message, parse_mode="Markdown")
	
	core.send_message(msg.chat.id, message, parse_mode="Markdown")

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}