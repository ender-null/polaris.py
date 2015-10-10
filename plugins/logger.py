from __main__ import *
from utilies import *

triggers = {
	''
}

def action(msg):
	if msg.chat.id != config.admin_group:
		user_firstname = msg.from_user.first_name
		user_id = str(msg.from_user.id)
		user_name = msg.from_user.username
		if msg.chat.id != msg.from_user.id:
			if hasattr(msg.chat, 'title'):
				user_chat = msg.chat.title
				user_chat_id = str(msg.chat.id)
			else:
				user_chat = msg.chat.first_name
				user_chat_id = str(msg.chat.id)
		
		message = msg.text.replace(bot.first_name + ' ', '')
		message += '\n------------------------\n'
		if hasattr(msg.from_user, 'username'):
			message += '*Name*: [' + user_firstname + '](http://telegram.me/' + user_name + ')\n'
		else:
			message += '*Name*: ' + user_firstname + '\n'
		message += '*User ID*: ' + user_id + '\n'
		if msg.chat.id != msg.from_user.id:
			message += '*Chat*: ' + user_chat + '\n'
			message += '*Chat ID*: ' + user_chat_id + '\n'
		message += '*Message ID*: ' + str(msg.message_id)
		
		core.send_message(config.admin_group, message, parse_mode="Markdown")
		
	else:
		if hasattr(msg, 'reply_to_message') and msg.reply_to_message.from_user.id == bot.id:
			message_id = last_word(msg.reply_to_message.text.split('\n')[-1])
			chat_id = last_word(msg.reply_to_message.text.split('\n')[-2])
			core.send_message(chat_id, msg.text, reply_to_message_id=message_id)

plugin = {
    'triggers': triggers,
    'action': action,
}