from core.utils import *
from threading import Thread
import re

def start():
    setup()

    bot.bindings.init()

    while (started):
        message = inbox.get()

        if message.type == 'text':
            if message.receiver.id > 0:
                print('\nGOT MESSAGE: [{0}] {1}'.format(message.receiver.first_name, message.content))
            else:
                print('\nGOT MESSAGE: [{0}] {1}'.format(message.receiver.title, message.content))
        else:
            if message.receiver.id > 0:
                print('\nGOT MESSAGE: [{0}] <{1}>'.format(message.receiver.first_name, message.type))
            else:
                print('\nGOT MESSAGE: [{0}] <{1}>'.format(message.receiver.title, message.type))

        for plugin in plugins:
            for command in plugin.commands:
                trigger = command.replace("/", config.start)

                if re.compile(trigger).search(message.content.lower()):
                    try:
                        plugin.run(message)
                    except Exception as e:
                        send_exc(message, e)


def setup():
    print('Loading configuration...')
    config.load(config)
    users.load(users)
    groups.load(groups)

    if not config.keys.bot_api_token and not config.keys.tg_cli_port:
        print('\nBindings not configured!')
        print('\tSelect the bindings to use:\n\t\t0. Telegram Bot API\n\t\t1. Telegram-CLI')
        frontend = input('\tBindings: ')
        if frontend == '1':
            config.keys.tg_cli_port = input('\tTelegram-CLI port: ')
            config.bindings = 'tg'
        else:
            config.keys.bot_api_token = input('\tTelegram Bot API token: ')
            config.bindings = 'api'
        config.plugins = list_plugins()
        config.save(config)
    else:
        if config.bindings == 'api' and config.keys.bot_api_token:
            print('\nUsing Telegram Bot API token: {}'.format(config.keys.bot_api_token))
        elif config.bindings == 'tg' and config.keys.tg_cli_port:
            print('\nUsing Telegram-CLI port: {}'.format(config.keys.tg_cli_port))

    load_plugins()

    bot.set_bindings(config.bindings)


def list_plugins():
    list = []
    for file in os.listdir('plugins'):
        if file.endswith('.py'):
            list.append(file.rstrip('.py'))
    return list


def load_plugins():
    print('\nLoading plugins...')
    for plugin in config.plugins:
        try:
            plugins.append(importlib.import_module('plugins.' + plugin))
            print('\t[OK] ' + plugin)
        except Exception as e:
            print('\t[Failed] ' + plugin + ': ' + str(e))

    print('\tLoaded: ' + str(len(plugins)) + '/' + str(len(config.plugins)))
    return plugins
