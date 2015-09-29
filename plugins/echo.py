import __main__
import utilies

doc = '/echo <text>\nRepeat a string.'
triggers = {
	'^/echo'
}

def action(msg):			
	input = utilies.get_input(msg.text)
	
	if not input:
		return __main__.tb.send_message(msg.chat.id, doc)
	
	__main__.tb.send_message(msg.chat.id, input)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}