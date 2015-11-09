from __main__ import *
from utilies import *

commands = [
	'^run ',
	'^reload',
	'^msg ',
	'^stop'
]
description = 'Get list of basic information for all commands, or more detailed documentation on a specified command.'
typing = True
hidden = True

def action(msg):			
	input = get_input(msg.text)
	
	message = locale['default']['errors']['argument']
	
	if msg.from_user.id not in config['admin']:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['permission'])
	
	if msg.text.startswith(config['command_start'] + 'run'):
		message = subprocess.check_output(input, shell=True)
		
	elif msg.text.startswith(config['command_start'] + 'reload'):
		bot_init()
		message = 'Bot reloaded!'
		
	elif msg.text.startswith(config['command_start'] + 'msg'):
		chat_id = first_word(input)
		text = get_input(input)
		
		if not core.send_message(chat_id, text):
			return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['argument'], parse_mode="Markdown")
		return
			
	elif msg.text.startswith(config['command_start'] + 'stop'):
		is_started = False
		sys.exit()
		
	core.send_message(msg.chat.id, message, parse_mode="Markdown")