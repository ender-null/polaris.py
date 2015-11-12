from utilies import *

commands = [
	'',
]
hidden = True

def run(msg):
		if (msg['chat']['id'] == -27616291
		and not msg['text']
		and not hasattr(msg, 'text')
		and not hasattr(msg, 'new_chat_participant')
		and not hasattr(msg, 'left_chat_participant')):
			forward_message('@porndb',  msg['chat']['id'], msg['message_id'])