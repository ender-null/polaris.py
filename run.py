import utilies
import time
import datetime

utilies.bot_init()
last_update = 0

while utilies.is_started == True:
	result = utilies.get_updates(last_update+1)['result']
	for update in result:
		if update['update_id'] > last_update:
			last_update = update['update_id']
			utilies.on_message_receive(update['message'])

print('Halted.')
