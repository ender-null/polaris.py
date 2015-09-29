import utilies
import time
import datetime
version = '0.1'
	
utilies.bot_init()
last_update = 0
last_cron = time.mktime(datetime.datetime.now().timetuple())

while utilies.is_started == True:
	res = utilies.core.get_updates(last_update+1)
	
	if not res:
		print('\033[91mError getting updates.\033[0m')
	else:
		for v in res:
			if v.update_id > last_update:
				last_update = v.update_id
				if hasattr(v.message, 'text'):
					print '\033[94m' + v.message.from_user.first_name + '@' + str(v.message.chat.id) + ': ' + v.message.text + '\033[0m'
				utilies.on_msg_receive(v.message)

print('Halted.')