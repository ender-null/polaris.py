from __main__ import *
from utilies import *
from extra.chatterbotapi import ChatterBotFactory, ChatterBotType
from HTMLParser import HTMLParser

triggers = {
	'#BOT_NAME_LOWER',
}

def action(msg):
	input = msg.text.replace(bot.first_name + ' ', '')
		
	factory = ChatterBotFactory()
	bot_core = factory.create(ChatterBotType.CLEVERBOT)
	bot_session = bot_core.create_session()
	unescape = HTMLParser().unescape
	
	try:
		message = unescape(bot_session.think(input));
	except:
		message = '...'
	
	core.send_message(msg.chat.id, message)

plugin = {
    'triggers': triggers,
    'action': action,
	'typing': True,
}