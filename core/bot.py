from core.utils import *
from threading import Thread
from time import time
from time import sleep
import re


def start():
    setup()

    bot.wrapper.get_me()
    bot.started = True
    
    load_plugins()
    
    print('Account: [%s] %s (@%s)' % (bot.id, bot.first_name, bot.username))

    bot.inbox_listener = Thread(target=bot.wrapper.inbox_listener)
    bot.inbox_listener.daemon = True
    bot.outbox_listener = Thread(target=outbox_listener)
    bot.outbox_listener.daemon = True
    bot.start()

    cron_handler = Thread(target=handle_cron)
    cron_handler.daemon = True
    cron_handler.start()

    while (bot.started):
        message = inbox.get()
        handle_message(message)

    print('Halted.')


def setup():
    print('Loading configuration...')
    config.load(config)
    lang.load(lang)
    users.load(users)
    groups.load(groups)
    tags.load(tags)

    if not 'bot_api_token' in config.keys and not 'tg_cli_port' in config.keys:
        print('\nWrapper not configured!')
        print('\tSelect the wrapper to use:\n\t\t0. Telegram Bot API\n\t\t1. Telegram-CLI')
        wrapper = input('\nWrapper: ')
        if wrapper == '1':
            config.keys.tg_cli_port = input('\tTelegram-CLI port: ')
            config.wrapper = 'tg'
        else:
            config.keys.bot_api_token = input('\tTelegram Bot API token: ')
            config.wrapper = 'api'
        config.plugins = list_plugins()
        config.save(config)
    else:
        if config.wrapper == 'api' and config.keys.bot_api_token:
            print('\nUsing Telegram Bot API token: {}'.format(config.keys.bot_api_token))
        elif config.wrapper == 'tg' and config.keys.tg_cli_port:
            print('\nUsing Telegram-CLI port: {}'.format(config.keys.tg_cli_port))
            
    bot.set_wrapper(config.wrapper)


def list_plugins():
    list = []
    for file in os.listdir('plugins'):
        if file.endswith('.py'):
            list.append(file.replace('.py', ''))
    return sorted(list)


def load_plugins():
    print('\nLoading plugins...')
    del plugins[:]
    for plugin in config.plugins:
        try:
            plugins.append(importlib.import_module('plugins.' + plugin))
            print('\t[OK] %s ' % (plugin))
        except Exception as e:
            print('\t[Failed] %s: %s ' % (plugin, str(e)))

    print('\tLoaded: ' + str(len(plugins)) + '/' + str(len(config.plugins)))
    return plugins


def handle_message(message):
    if message.date < time() - 10:
            return
    
    if not is_trusted(message.sender.id):
        if message.receiver.id > 0:
            chat = message.sender.id
        else:
            chat = message.receiver.id
        
        # checks if the chat is special
        if (has_tag(chat, 'type:log') or has_tag(chat, 'type:alerts')):
            return

        # if chat or user is muted ignores the message
        if has_tag(message.sender.id, 'muted') or has_tag(message.receiver.id, 'muted'):
            return

    if message.receiver.id > 0:
        if message.sender.id > 0:
            print('[%s << %s <%s>] %s' % (message.receiver.first_name, message.sender.first_name, message.type, message.content))
        else:
            print('[%s << %s <%s>] %s' % (message.receiver.first_name, message.sender.title, message.type, message.content))
    else:
        if message.sender.id > 0:
            print('[%s << %s <%s>] %s' % (message.receiver.title, message.sender.first_name, message.type, message.content))
        else:
            print('[%s << %s <%s>] %s' % (message.receiver.title, message.sender.title, message.type, message.content))

    for plugin in plugins:
        if hasattr(plugin, 'process'):
            plugin.process(message)
            
        if hasattr(plugin, 'shortcut'):
            if type(plugin.shortcut) is not list:
                plugin.shortcut = [plugin.shortcut]
            for command in plugin.shortcut:
                if command and check_trigger(command, plugin, message):
                    break

        if hasattr(plugin, 'commands'):
            for command, parameters in plugin.commands:
                if check_trigger(command, plugin, message):
                    break


def check_trigger(command, plugin, message):
    trigger = command.replace('/', '^' + config.start)

    if message.content and re.compile(trigger).search(message.content.lower()):
        try:
            if hasattr(plugin, 'inline') and message.type == 'inline_query':
                return plugin.inline(message)
            else:
                return plugin.run(message)
        except:
            return send_exception(message)

def handle_cron():
    while (True):
        for plugin in plugins:
            if hasattr(plugin, 'cron'):
                try:
                    plugin.cron()
                except Exception as e:
                    send_exception(e)
        sleep(5)

def outbox_listener():
    color = Colors()
    while (True):
        message = outbox.get()
        try:
            if message.receiver.id > 0:
                if message.sender.id > 0:
                    print('>> [%s << %s <%s>] %s' % (message.receiver.first_name, message.sender.first_name, message.type, message.content))
                else:
                    print('>> [%s << %s <%s>] %s' % (message.receiver.first_name, message.sender.title, message.type, message.content))
            else:
                if message.sender.id > 0:
                    print('>> [%s << %s <%s>] %s' % (message.receiver.title, message.sender.first_name, message.type, message.content))
                else:
                    print('>> [%s << %s <%s>] %s' % (message.receiver.title, message.sender.title, message.type, message.content))
            bot.wrapper.send_message(message)
        except:
            return send_exception(message)
