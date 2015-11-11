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
	
	if not is_admin(msg):
		return send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['permission'])
	
	if get_command(msg.text) == 'run':
		message = subprocess.check_output(input, shell=True)
		
	elif get_command(msg.text) ==  'reload':
		bot_init()
		message = 'Bot reloaded!'
		
	elif get_command(msg.text) == 'msg':
		chat_id = first_word(input)
		text = get_input(input)
		
		if not core.send_message(chat_id, text):
			return send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['argument'], parse_mode="Markdown")
		return
			
	elif get_command(msg.text) == 'stop':
		is_started = False
		sys.exit()
		
	send_message(msg.chat.id, message, parse_mode="Markdown")