from core.shared import *
from threading import Thread
import requests

# Telegram Bot API bindings
api_url = 'https://api.telegram.org/bot' + config.keys.bot_api_token + '/'

def send_request(url, params=None, headers=None, files=None, data=None):
    # print('\tRequest: ' + url)

    result = requests.get(url, params=params, headers=headers, files=files, data=data)

    if result.status_code != 200:
        print('NOT OK')
        print(result.text)
        return False

    # print(result.text)

    return json.loads(result.text)


def api_request(api_method, params=None, headers=None, files=None):
    url = api_url + api_method

    return send_request(url, params, headers, files)


def get_updates(offset=None, limit=None, timeout=None):
    params = {}
    if offset:
        params['offset'] = offset
    if limit:
        params['limit'] = limit
    if timeout:
        params['timeout'] = timeout
    return api_request('getUpdates', params)


def get_me():
    result = api_request('getMe')
    bot.first_name = result['result']['first_name']
    bot.username = result['result']['username']
    bot.id = result['result']['id']


def send_message(message):
    if message.type == 'text':
        params = {
            'chat_id': message.receiver.id,
            'text': message.content
        }
        api_request('sendMessage', params)


def inbox_listen():
    print('\tStarting inbox daemon...')
    last_update = 0

    while (True):
        updates = get_updates(last_update + 1)
        result = updates['result']

        if result:
            for update in result:
                if update['update_id'] > last_update:
                    last_update = update['update_id']
                    msg = update['message']

                    if (not 'inline_query' in update and 'text' in msg):
                        # Generates a Message object and sends it to the inbox queue.
                        id = msg['message_id']
                        if msg['chat']['id'] > 0:
                            receiver = User
                            receiver.first_name = msg['chat']['first_name']
                            if 'last_name' in msg['from']:
                                receiver.last_name = msg['chat']['last_name']
                            receiver.username = msg['chat']['username']
                        else:
                            receiver = Group
                            receiver.title = msg['chat']['title']
                        receiver.id = msg['chat']['id']
                        sender = User
                        sender.id = msg['from']['id']
                        sender.first_name = msg['from']['first_name']
                        if hasattr(msg['from'], 'last_name'):
                            sender.last_name = msg['from']['last_name']
                        sender.username = msg['from']['username']
                        content = msg['text']
                        date = msg['date']

                        message = Message(id, sender, receiver, content, date)
                        inbox.put(message)


def outbox_listen():
    while (True):
        message = outbox.get()
        print('OUTBOX: ' + message.content)
        send_message(message)


inbox_listener = Thread(target=inbox_listen, name='Inbox Listener')
outbox_listener = Thread(target=outbox_listen, name='Outbox Listener')


def init():
    print('\nInitializing Telegram Bot API...')
    get_me()
    print('\tUsing: {0} (@{1})'.format(bot.first_name, bot.username))

    inbox_listener.start()
    outbox_listener.start()
