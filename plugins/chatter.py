from __main__ import *
from utilies import *
import cleverbot
from HTMLParser import HTMLParser

triggers = {
	'#BOT_NAME_LOWER',
}

typing = True

def action(msg):
	input = msg.text.replace(bot.first_name + ' ', '')
	
	cb = cleverbot.Cleverbot()	
	unescape = HTMLParser().unescape
	
	try:
		message = unescape(cb.ask(input))
	except:
		message = '...'
		
	core.send_message(msg.chat.id, message)