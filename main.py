from polaris import utils, types, bot
import os, logging, time, importlib


# Loads the bots from the /bots/ #
def get_bots():
    botlist = []

    for filename in os.listdir('bots'):
        if filename.endswith('.json'):
            botlist.append(bot.Bot(filename[:-5]))

    return botlist


# Adds, removes and configures bots #
def setup():
    logging.warning('BOT SETUP NOT YET IMPLEMENTED')


# Loads all plugins from /polaris/plugins/ #
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


logging.info('Looking for bot configurations in "bots" folder...')
botlist = get_bots()

setup()

try:
    for bot in botlist:
        logging.info('Initializing [%s] bot...' % bot.name)
        bot.start()

    while True:
        exited = 0
        for bot in botlist:
            if not bot.started:
                exited += 1
            time.sleep(1)

        if exited == len(botlist):
            logging.info('All bots have exited, finishing.')
            break

except KeyboardInterrupt:
    for bot in botlist:
        logging.info('Exiting [%s] bot...' % bot.name)
