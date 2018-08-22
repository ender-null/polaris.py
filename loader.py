from polaris.types import AutosaveDict
from polaris.bot import Bot
from polaris.utils import set_logger, load_plugin_list, catch_exception, wait_until_received
from multiprocessing import Process
from time import sleep
from firebase_admin import credentials, db, storage
import firebase_admin
import os, logging, importlib

# Loads the bots from the /bots/ #
def get_bots():
    botlist = []

    for bot in bots:
        try:
            botlist.append(Bot(bot))
        except Exception as e:
            catch_exception(e)
            logging.error('  [Failed] "%s" failed to initialize' % bot)

    return botlist


# Imports all plugin modules to a list. #
def import_plugins(enabled_plugins):
    plugins = []
    logging.debug('Importing plugins...')

    for plugin in enabled_plugins:
        try:
            plugins.append(importlib.import_module('polaris.plugins.' + plugin))
            logging.debug('  [OK] %s ' % (plugin))
        except Exception as e:
            logging.error('  [Failed] %s: %s ' % (plugin, str(e)))

    logging.info('  Loaded: ' + str(len(plugins)) + '/' + str(len(enabled_plugins)))

    return plugins


# EXPERIMENTAL!! Adds, removes and configures bots #
def setup():
    def bot_config(name):
        config = AutosaveDict('bots/%s.json' % name)

        i = 1
        finished = False
        while not finished:
            text = 'Editing /bots/%s.json\n' % name

            if 'bindings' in config:
                bindings = config['bindings']
            else:
                bindings = 'telegram-bot-api'

            if 'bindings_token' in config:
                bindings_token = config['bindings_token']
            else:
                bindings_token = 'YOUR TELEGRAM BOT TOKEN'

            if 'command_start' in config:
                command_start = config['command_start']
            else:
                command_start = '/'

            if 'owner' in config:
                owner = config['owner']
            else:
                owner = 0

            if 'debug' in config:
                debug = config['debug']
            else:
                debug = False

            if 'language' in config:
                language = config['language']
            else:
                language = 'default'

            if 'plugins' in config:
                plugins = config['plugins']
            else:
                plugins = load_plugin_list()

            if 'api_keys' in config:
                api_keys = config['api_keys']
            else:
                api_keys = {}

            text += '(0) Finish editing\n'
            text += '(1) bindings: %s\n' % bindings
            text += '(2) bindings_token: %s\n' % bindings_token
            text += '(3) command_start: %s\n' % command_start
            text += '(4) owner: %s\n' % owner
            text += '(5) debug: %s\n' % debug
            text += '(6) language: %s\n' % language
            text += '(7) plugins: %s\n' % plugins
            text += '(8) api_keys: %s\n' % api_keys

            option = int(input(text))
            if option == 0:
                print('Saving all values to "bots/%s.json".' % name)
                config.bindings = bindings
                config.bindings_token = bindings_token
                config.command_start = command_start
                config.owner = owner
                config.debug = debug
                config.language = language
                config.plugins = plugins
                config.api_keys = api_keys
                finished = True

            elif option == 1:
                option = input('What bindings want to use? (Current value: "%s")\n' % bindings)
                config.bindings = option


    logging.warning('BOT SETUP NOT YET IMPLEMENTED')
    botlist = []
    for filename in os.listdir('bots'):
        if filename.endswith('.json'):
            botlist.append(filename[:-5])

    logging.info('Found %s bots configuration files.' % len(botlist))
    user_input = input('Want to edit them or set up another one? (y)es / (n)o\n')
    if user_input.lower() == 'y' or user_input.lower() == 'yes':
        ok = False
        while not ok:
            user_input = input('Edit existing bot configuration or add a new one? (e)dit / (a)dd / (r)emove / (f)inish\n')
            if user_input.lower() == 'e' or user_input.lower() == 'edit':
                ok = True

                bots = 'What bot config want to edit?\n'
                botlist = []
                for filename in os.listdir('bots'):
                    if filename.endswith('.json'):
                        botlist.append(filename[:-5])
                        bots += '\t(%s) %s\n' % (len(botlist), botlist[len(botlist)-1])

                user_input = input(bots)
                bot_config(botlist[int(user_input)-1])

            elif user_input.lower() == 'a' or user_input.lower() == 'add':
                ok = True
                name = input('How do you want to name the new bot? (lowercase alphanumeric characters, please)\n')
                bot_config(name)

            elif user_input.lower() == 'f' or user_input.lower() == 'finish':
                ok = True
                logging.info('Let\'s Go!')

            elif user_input.lower() == 'r' or user_input.lower() == 'remove':
                ok = True

                bots = 'What bot config want to REMOVE?\n'
                botlist = []
                for filename in os.listdir('bots'):
                    if filename.endswith('.json'):
                        botlist.append(filename[:-5])
                        bots += '\t(%s) %s\n' % (len(botlist), botlist[len(botlist)-1])

                user_input = input(bots)
                os.remove('bots/%s.json' % botlist[int(user_input)-1])
                print('Removed "bots/%s.json".' % botlist[int(user_input)-1])


# Now let's start doing stuff. #
# setup()
set_logger()
cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://polaris-bot.firebaseio.com/',
    'storageBucket': 'polaris-bot.appspot.com'
})

bots = wait_until_received('bots')

logging.info('Looking for bot configurations in Firebase...')
botlist = get_bots()

try:
    for bot in botlist:
        logging.info('Initializing [%s] bot...' % bot.name)
        bot.start()

    while True:
        exited = 0
        for bot in botlist:
            if not bot.started:
                exited += 1
            sleep(1)

        if exited == len(botlist):
            logging.info('All bots have exited, finishing.')
            break

except KeyboardInterrupt:
    for bot in botlist:
        logging.debug('Exiting [%s] bot...' % bot.name)
        bot.started = False
