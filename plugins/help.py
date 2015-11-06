from __main__ import *
from utilies import *

commands = [
	'^help',
	'^h$'
]
parameters = (
	('command', False),
)
description = 'Get list of basic information for all commands, or more detailed documentation on a specified command.'
typing = True

def action(msg):			
	input = get_input(msg.text)
	
	if input:
		for i,v in plugins.items():
			if not hasattr(v, 'hidden'):
				if config['command_start'] + input == v.commands[0].replace('^', '#'):
					doc = config['command_start'] + v.commands[0].replace('^', '')
					if hasattr(v, 'parameters'):
						for parameter,required in v.parameters:
							if required == True:
								doc += ' *[' + parameter + ']*'
							else:
								doc += ' _[' + parameter + ']_'
					doc += '\n' + v.description
					return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	else:
		help = ''
		for i,v in plugins.items():
			if not hasattr(v, 'hidden'):
				help += '\t' + config['command_start']
				help += v.commands[0].replace('^', '')
				
				if hasattr(v, 'parameters'):
					for parameter,required in v.parameters:
						if required == True:
							help += ' *[' + parameter + ']*'
						else:
							help += ' _[' + parameter + ']_'
				help += '\n'
			
		message = '*Commands*:\n' + help
		
		if msg.from_user.id != msg.chat.id:
			if not core.send_message(msg.from_user.id, message, parse_mode="Markdown"):
				return core.send_message(msg.chat.id, message, parse_mode="Markdown")
			return core.send_message(msg.chat.id, 'I have sent it in a *private message*.', parse_mode="Markdown")
		else:
			return core.send_message(msg.chat.id, message, parse_mode="Markdown")