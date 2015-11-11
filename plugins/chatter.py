from __main__ import *
from utilies import *
import cleverbot
from HTMLParser import HTMLParser

commands = [
	'#BOT_NAME_LOWER'
]
description = 'Get list of basic information for all commands, or more detailed documentation on a specified command.'
hidden = True

def action(msg):
	input = msg['text'].replace(bot['first_name'] + ' ', '')
	
	cb = cleverbot.Cleverbot()	
	unescape = HTMLParser().unescape
	
	try:
		message = unescape(cb.ask(input))
	except:
		message = '...'
		
	send_message(msg['chat']['id'], message)