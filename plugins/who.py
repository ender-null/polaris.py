from __main__ import *
from utilies import *

doc = config.command_start + 'who\nGets user info.'
triggers = {
	'^' + config.command_start + 'who'
}

def action(msg):			
	user_firstname = msg.from_user.first_name
	user_id = str(msg.from_user.id)
	user_name = msg.from_user.username
	if hasattr(msg.chat, 'title'):
		user_chat = msg.chat.title
		user_chat_id = str(msg.chat.id)
	else:
		user_chat = msg.chat.first_name
		user_chat_id = str(msg.chat.id)
	
	if hasattr(msg, 'reply_to_message'):
		user_firstname = msg.reply_to_message.from_user.first_name
		user_id = str(msg.reply_to_message.from_user.id)
		user_name = msg.reply_to_message.from_user.username
		if hasattr(msg.reply_to_message.chat, 'title'):
			user_chat = msg.reply_to_message.chat.title
			user_chat_id = str(msg.reply_to_message.chat.id)
		else:
			user_chat = msg.reply_to_message.chat.first_name
			user_chat_id = str(msg.reply_to_message.chat.id)
	
	message = '#GREETING, I am *#BOT_FIRSTNAME* and you are *' + user_firstname + '*.\n\n'
	message += '*Username*: @' + user_name + '\n'
	message += '*User ID*: ' + user_id + '\n'
	message += '*Chat*: ' + user_chat + '\n'
	message += '*Chat ID*: ' + user_chat_id + ''
	
	message = tag_replace(message, msg)
	
	core.send_message(msg.chat.id, message, parse_mode="Markdown")

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}