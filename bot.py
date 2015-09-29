import telebot
import importlib
import time
import datetime
import re
import sys

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
				print '\033[93m\tTrigger: ' + t + '\033[0m'
				if hasattr(v, 'typing'):
					tb.send_chat_action(msg.chat.id, 'typing')
					
				try:	
					v.action(msg)
				except Exception as e:
					tb.send_message(msg.chat.id, str(e))

def bot_init():
	print sys.getdefaultencoding()
	print('\033[1mLoading configuration...\033[0m')

	import config
	import utilies

	print('\033[1mFetching bot information...\033[0m')
	global tb
	tb = telebot.TeleBot(config.apis['telegram_bot'])
	
	global bot
	bot = tb.get_me()
	while bot == False:
		print('\033[91mFailure fetching bot information. Trying again...\033[0m')
		bot = tb.get_me()

	print('\033[1mLoading plugins...\033[0m')
	global plugins
	plugins = {}
		
	plugins = utilies.load_plugins()

	print('\033[1mPlugins loaded: ' + str(len(plugins)) + '.\nGenerating help message...\033[0m')

	global help_message
	help_message = ''
	for i,v in plugins.items():
		if hasattr(v, 'doc'):
			a = v.doc.splitlines()[0]
			help_message = help_message + a + '\n'
	
	print('\033[95m\n@' + str(bot.username) + ', AKA ' + str(bot.first_name) + ' (' + str(bot.id) + ')\033[0m')

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
		print('\033[91mError getting updates.\033[0m')
	else:
		for v in res:
			if v.update_id > last_update:
				last_update = v.update_id
				if hasattr(v.message, 'text'):
					print '\033[94m' + v.message.from_user.first_name + '@' + str(v.message.chat.id) + ': ' + v.message.text + '\033[0m'
				on_msg_receive(v.message)

print('\033[92mHalted.\033[0m')