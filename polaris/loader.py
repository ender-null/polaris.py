from polaris import bot
import os, logging, importlib

def get_bots():
    botlist = []

    for filename in os.listdir('bots'):
        if filename.endswith('.json'):
            botlist.append(bot.Bot(filename[:-5]))

    return botlist

def setup():
    logging.warning('BOT SETUP NOT YET IMPLEMENTED')

def load_plugins():
    plugin_list = []
    for file in os.listdir('polaris/plugins'):
        if file.endswith('.py'):
            plugin_list.append(file.replace('.py', ''))
    return sorted(plugin_list)

def import_plugins(enabled_plugins):
    plugins = []
    logging.info('Importing plugins...')

    for plugin in enabled_plugins:
        try:
            plugins.append(importlib.import_module('polaris.plugins.' + plugin))
            logging.info('  [OK] %s ' % (plugin))
        except Exception as e:
            logging.error('  [Failed] %s: %s ' % (plugin, str(e)))

    logging.info('  Loaded: ' + str(len(plugins)) + '/' + str(len(enabled_plugins)))

    return plugins
