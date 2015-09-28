import telebot
import importlib
import time
import datetime
import re

VERSION = '0.1'
 
def on_msg_receive(msg):
	
 	msg = process_msg(msg)
	
 	if msg.date < time.mktime(datetime.datetime.now().timetuple()) - 10:
 		return
 	if not hasattr(msg, 'text'):
 		return

 	lower = msg.text.lower()

	for i,v in plugins.items():
		for t in v.triggers:
			if re.compile(t).search(lower):
				print '\tTrigger: ' + t
				if hasattr(v, 'typing'):
					tb.send_chat_action(msg.chat.id, 'typing')
					
				v.action(msg)
 	
def bot_init():
	print('Loading configuration...')

	import config
	import utilies

	print('Fetching bot information...')
	global tb
	tb = telebot.TeleBot(config.apis['telegram_bot'])
	
	global bot
	bot = tb.get_me()
	while bot == False:
		print('Failure fetching bot information. Trying again...')
		bot = tb.get_me()

	print('Loading plugins...')
	global plugins
	plugins = {}
		
	plugins = utilies.load_plugins()

	print('\nPlugins loaded: ' + str(len(plugins)) + '.\nGenerating help message...')

	global help_message
	help_message = ''
	for i,v in plugins.items():
		if hasattr(v, 'doc'):
			a = v.doc.splitlines()[0]
			help_message = help_message + a + '\n'
	
	print('\n@' + str(bot.username) + ', AKA ' + str(bot.first_name) + ' (' + str(bot.id) + ')')

	global is_started
 	is_started = True
 	
def process_msg(msg):
	if hasattr(msg, 'new_chat_participant'):
		if msg.new_chat_participant.id != bot.id:
			msg.text = 'hi ' + str(bot.first_name)
			msg.from_user = msg.new_chat_participant
		else:
			msg.text = '/about'

	if hasattr(msg, 'left_chat_participant'):
		if msg.left_chat_participant.id != bot.id:
			msg.text = 'bye ' + str(bot.first_name)
			msg.from_user = msg.left_chat_participant
	return msg
	
bot_init()
last_update = 0
last_cron = time.mktime(datetime.datetime.now().timetuple())

while is_started == True:
	res = tb.get_updates(last_update+1)
	
	if not res:
		print('\tError getting updates.')
	else:
		for v in res:
			if v.update_id > last_update:
				last_update = v.update_id
				if hasattr(v.message, 'text'):
					print 'Message: ' + v.message.from_user.first_name + ' - ' + v.message.text
				on_msg_receive(v.message)

print('Halted.')