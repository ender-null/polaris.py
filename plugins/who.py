from __main__ import *
from utilies import *

doc = config.command_start + 'who\nGets user info.'

triggers = {
	'^' + config.command_start + 'who'
}

typing = True

def action(msg):			
	
	if hasattr(msg, 'reply_to_message'):
		msg.from_user = msg.reply_to_message.from_user
		msg.chat = msg.reply_to_message.chat
	
	message = '#GREETING, I am *#BOT_FIRSTNAME* and you are *' + msg.from_user.first_name + '*.\n\n'.replace("_", "\_")
	if msg.from_user.username:
		message += '*Username*: @' + msg.from_user.username.replace("_", "\_") + '\n'
	message += '*User ID*: ' + str(msg.from_user.id) + '\n'
	if msg.chat.type == 'group':
		message += '*Chat*: ' + msg.chat.title.replace("_", "\_") + '\n'
		message += '*Chat ID*: ' + str(msg.chat.id) + ''
	
	message = tag_replace(message, msg)
	
	core.send_message(msg.chat.id, message, parse_mode="Markdown")
