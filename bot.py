import utilies
import time
import datetime
version = '0.1'
	
utilies.bot_init()
last_update = 0

while utilies.is_started == True:
	#try:
		result = utilies.core.get_updates(last_update+1)
		if not result:
			print('Error getting updates.')
		else:
			for update in result:
				if update.update_id > last_update:
					last_update = update.update_id
					utilies.on_message_receive(update.message)
	#except Exception as e:
	#	utilies.core.send_message(14143244, str(e))

print('Halted.')
