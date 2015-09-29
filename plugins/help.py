import __main__
import utilies

doc = '/help [command]\nGet list of basic information for all commands, or more detailed documentation on a specified command.'
triggers = {
	'^/help',
	'^/h$',
	'^/start$'
}

def action(msg):			
	input = utilies.get_input(msg.text)
	
	'''
	if input:
		for v in __main__.plugins:
			if hasattr(v, 'doc'):
				if '/' + input == v.doc:
					return __main__.tb.send_message(msg.chat.id, v.doc)
	'''
	
	help_message = ''
	for k,v in __main__.plugins.items():
		if hasattr(v, 'doc'):
			a = '\t' + v.doc.split('\n', 1)[0]
			help_message = help_message + a + '\n'
	
	message = 'Commands:\n' + help_message
	
	if msg.from_user.id != msg.chat.id:
		if not send_message(msg.from_user.id, message):
			return __main__.tb.send_message(msg.chat.id, message)
		return __main__.tb.send_message(msg.chat.id, 'I have sent you the requested information in a private message.')
	else:
		return __main__.tb.send_message(msg.chat.id, message)
	
	__main__.tb.send_message(msg.chat.id, message)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}