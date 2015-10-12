from __main__ import *
from utilies import *
from extra.chatterbotapi import ChatterBotFactory, ChatterBotType
from HTMLParser import HTMLParser

triggers = {
	'#BOT_NAME_LOWER',
}

typing = True

def action(msg):
	input = msg.text.replace(bot.first_name + ' ', '')
		
	factory = ChatterBotFactory()
	bot_core = factory.create(ChatterBotType.CLEVERBOT)
	bot_session = bot_core.create_session()
	unescape = HTMLParser().unescape
	
	try:
		message = unescape(bot_session.think(input))
		core.send_message(msg.chat.id, message)
	except:
		pass