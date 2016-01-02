import utils
import time
import datetime

utils.bot_init()
last_update = 0
last_cron = utils.now()

while utils.is_started:
    result = utils.get_updates(last_update + 1)['result']
    if result:
        for update in result:
            if update['update_id'] > last_update:
                last_update = update['update_id']
                if 'message' in update:
                    utils.on_message_receive(update['message'])
                else:
                    utils.on_query_receive(update['inline_query'])

    if last_cron < utils.now() - 5:
        for i, plugin in utils.plugins.items():
            if hasattr(plugin, 'cron'):
                try:
                    plugin.cron()
                except Exception as e:
                    send_exception(e)
print('Halted.')
