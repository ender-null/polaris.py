from __main__ import *
from utilies import *

commands = [
	'^who'
]
description = 'Gets user info.'
action = 'typing'

def run(msg):			
	
	if hasattr(msg, 'reply_to_message'):
		msg['from'] = msg['reply_to_message']['from']
		msg['chat'] = msg['reply_to_message']['chat']
	
	message = '#GREETING, I am *#BOT_FIRSTNAME* and you are *' + escape_markup(msg['from']['first_name']) + '*.\n\n'
	if msg['from']['username']:
		message += '*Username*: @' + escape_markup(msg['from']['username']) + '\n'
	message += '*User ID*: ' + str(msg['from']['id']) + '\n'
	if msg['chat']['type'] == 'group':
		message += '*Chat*: ' + escape_markup(msg['chat']['title']) + '\n'
		message += '*Chat ID*: ' + str(msg['chat']['id']) + ''
	
	message = tag_replace(message, msg)
	
	send_message(msg['chat']['id'], message, parse_mode="Markdown")
