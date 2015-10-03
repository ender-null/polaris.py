import utilies
import time
import datetime
version = '0.1'
	
utilies.bot_init()
last_update = 0
last_cron = time.mktime(datetime.datetime.now().timetuple())

while utilies.is_started == True:
	try:
		res = utilies.core.get_updates(last_update+1)
		if not res:
			print('\033[91mError getting updates.\033[0m')
		else:
			for v in res:
				if v.update_id > last_update:
					last_update = v.update_id
					utilies.on_msg_receive(v.message)
	except Exception as e:
		utilies.core.send_message(14143244, str(e))

print('Halted.')
