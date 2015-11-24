import utilies
import time
import datetime

utilies.bot_init()
last_update = 0
last_cron = utilies.now()

while utilies.is_started:
    result = utilies.get_updates(last_update + 1)['result']
    if result:
        for update in result:
            if update['update_id'] > last_update:
                last_update = update['update_id']
                utilies.on_message_receive(update['message'])

    if last_cron < utilies.now() - 5:
        for i, plugin in utilies.plugins.items():
            if hasattr(plugin, 'cron'):
                try:
                    plugin.cron()
                except Exception as e:
                    send_exception(e)
print('Halted.')
