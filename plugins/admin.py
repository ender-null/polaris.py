from __main__ import *
from utilies import *

triggers = {
	'^' + config['command_start'] + 'run ',
	'^' + config['command_start'] + 'reload',
	'^' + config['command_start'] + 'msg ',
	'^' + config['command_start'] + 'stop',
}

typing = True

def action(msg):			
	input = get_input(msg.text)
	
	message = locale['default']['errors']['argument']
	
	if msg.from_user.id not in config['admin']:
		return core.send_message(msg.chat.id, locale['default']['errors']['permission'])
	
	if msg.text.startswith(config['command_start'] + 'run'):
		message = subprocess.check_output(input, shell=True)
		
	elif msg.text.startswith(config['command_start'] + 'reload'):
		bot_init()
		message = 'Bot reloaded!'
		
	elif msg.text.startswith(config['command_start'] + 'msg'):
		chat_id = first_word(input)
		text = get_input(input)
		
		if not core.send_message(chat_id, text):
			return core.send_message(msg.chat.id, locale['default']['errors']['argument'], parse_mode="Markdown")
		return
			
	elif msg.text.startswith(config['command_start'] + 'stop'):
		is_started = False
		sys.exit()
		
	core.send_message(msg.chat.id, message, parse_mode="Markdown")