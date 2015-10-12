import utilies as u
import time
import datetime
import web

version = '0.1'
u.bot_init()
last_update = 0

while u.is_started == True:
	result = u.core.get_updates(last_update+1)
	if not result:
		print('Error getting updates.')
	else:
		for update in result:
			if update.update_id > last_update:
				last_update = update.update_id
				u.on_message_receive(update.message)

print('Halted.')
