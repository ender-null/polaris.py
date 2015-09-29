import __main__
import utilies

doc = '/echo *[text]*\nRepeat a string.'
triggers = {
	'^/echo'
}

def action(msg):			
	input = utilies.get_input(msg.text)
		
	if not input:
		return __main__.tb.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	__main__.tb.send_message(msg.chat.id, input, parse_mode="Markdown")

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}