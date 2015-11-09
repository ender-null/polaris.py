from __main__ import *
from utilies import *

commands = [
	'^who'
]
description = 'Gets user info.'
typing = True

def action(msg):			
	
	if hasattr(msg, 'reply_to_message'):
		msg.from_user = msg.reply_to_message.from_user
		msg.chat = msg.reply_to_message.chat
	
	message = '#GREETING, I am *#BOT_FIRSTNAME* and you are *' + escape_markup(msg.from_user.first_name) + '*.\n\n'
	if msg.from_user.username:
		message += '*Username*: @' + escape_markup(msg.from_user.username) + '\n'
	message += '*User ID*: ' + str(msg.from_user.id) + '\n'
	if msg.chat.type == 'group':
		message += '*Chat*: ' + escape_markup(msg.chat.title) + '\n'
		message += '*Chat ID*: ' + str(msg.chat.id) + ''
	
	message = tag_replace(message, msg)
	
	core.send_message(msg.chat.id, message, parse_mode="Markdown")
