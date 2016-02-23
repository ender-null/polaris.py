from core.shared import *
from core.utils import *
from threading import Thread
import re


def listen():
    while (True):
        message = inbox.get()
        print('GOT MESSAGE: ' + message.content)
        for plugin in plugins:
            for command in plugin.commands:
                trigger = command.replace("/", config.start)

                if re.compile(trigger).search(message.content.lower()):
                    try:
                        plugin.run(message)
                    except Exception as e:
                        send_exc(message, e)


def start():
    setup()

    bot.bindings.init()

    listener = Thread(target=listen, name='Listener')
    listener.start()


def setup():
    print('Loading configuration...')
    config.load(config)
    users.load(users)
    groups.load(groups)

    load_plugins()

    if not config.keys.bot_api_token and not config.keys.tg_cli_port:
        print('\nFrontend not configured!')
        print('\tSelect the Frontend to use:\n\t\t0. Telegram Bot API\n\t\t1. Telegram-CLI')
        frontend = input('\tFrontend: ')
        if frontend == '1':
            config.keys.tg_cli_port = input('\tTelegram-CLI port: ')
            config.bindings = 'tg'
        else:
            config.keys.bot_api_token = input('\tTelegram Bot API token: ')
            config.bindings = 'api'
        config.save(config)
    else:
        if config.keys.bot_api_token:
            print('\nUsing Telegram Bot API token: {}'.format(config.keys.bot_api_token))
        elif config.keys.tg_cli_port:
            print('\nUsing Telegram-CLI port: {}'.format(config.keys.tg_cli_port))

    bot.set_bindings(config.bindings)


def load_plugins():
    print('Loading plugins...')
    for plugin in config.plugins:
        try:
            plugins.append(importlib.import_module('plugins.' + plugin))
            print('\t[OK] ' + plugin)
        except Exception as e:
            print('\t[Failed] ' + plugin + ': ' + str(e))

    print('\n\tLoaded: ' + str(len(plugins)) + '/' + str(len(config.plugins)))
    return plugins
