from core.shared import *
import json
from collections import OrderedDict
import importlib


# Used to store the bindings module and the User data of the bot.
class Bot:
    bindings = None
    id = None
    first_name = None
    last_name = None
    username = None

    def set_bindings(self, bindings='api'):
        self.bindings = importlib.import_module('core.bindings.' + bindings)


# Defines the structure of the User objects.
class User:
    id = None
    first_name = None
    last_name = None
    username = None

    def __init__(self, id, first_name, last_name, username):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


# Defines the structure of the Group objects.
class Group:
    id = None
    title = None

    def __init__(self, id, title):
        self.id = id
        self.title = title


# This classes define and manage configuration files and stored data.
class Config:
    # Main configuration file.
    class Config:
        # Keys store the API keys.
        class Keys:
            bot_api_token = None
            tg_cli_port = None
            cat_api = None
            giphy = None
            league_of_legends = None
            openweathermap = None
            google_developer_console = None
            azure_key = None

        bindings = None
        owner = None
        keys = Keys
        plugins = []
        start = '/'

        def load(self):
            try:
                with open('data/config.json', 'r') as f:
                    config_json = json.load(f, object_pairs_hook=OrderedDict)
                    keys = Config.Config.Keys
                    keys.bot_api_token = config_json['keys']['bot_api_token']
                    keys.tg_cli_port = config_json['keys']['tg_cli_port']
                    keys.cat_api = config_json['keys']['cat_api']
                    keys.giphy = config_json['keys']['giphy']
                    keys.league_of_legends = config_json['keys']['league_of_legends']
                    keys.openweathermap = config_json['keys']['openweathermap']
                    keys.google_developer_console = config_json['keys']['google_developer_console']
                    keys.azure_key = config_json['keys']['azure_key']

                    self.bindings = config_json['bindings']
                    self.owner = config_json['owner']
                    self.keys = keys
                    self.plugins = config_json['plugins']
                    self.start = config_json['start']
                    print('\t[OK] ' + 'config.json loaded.')
            except:
                keys = Config.Config.Keys
                keys.bot_api_token = None
                keys.tg_cli_port = None
                keys.cat_api = None
                keys.giphy = None
                keys.league_of_legends = None
                keys.openweathermap = None
                keys.google_developer_console = None
                keys.azure_key = None
                self.keys = keys
                print('\t[Failed] ' + 'config.json NOT loaded.')

        def save(self):
            try:
                with open('data/config.json', 'w') as f:
                    keys_tuples = (
                        ('bot_api_token', self.keys.bot_api_token),
                        ('tg_cli_port', self.keys.tg_cli_port),
                        ('cat_api', self.keys.cat_api),
                        ('giphy', self.keys.giphy),
                        ('league_of_legends', self.keys.league_of_legends),
                        ('openweathermap', self.keys.openweathermap),
                        ('google_developer_console', self.keys.google_developer_console),
                        ('azure_key', self.keys.azure_key)
                    )

                    config_tuples = (
                        ('bindings', self.bindings),
                        ('owner', self.owner),
                        ('keys', OrderedDict(keys_tuples)),
                        ('plugins', self.plugins),
                        ('start', self.start)
                    )

                    config = OrderedDict(config_tuples)

                    json.dump(config, f, sort_keys=True, indent=4)
                    print('\t[OK] config.json saved.')
            except:
                print('\t[Failed] ' + 'config.json NOT saved.')

    # Defines a language for the messages.
    class Language:
        message = OrderedDict
        error = OrderedDict
        plugins = OrderedDict

    # Stores a list of data of users.
    class Users:
        items = None

        class User:
            first_name = None
            last_name = None
            username = None
            tags = None
            settings = None

            def __init__(self, first_name, last_name=None, username=None, tags=None, settings=None):
                self.first_name = first_name
                self.last_name = last_name
                self.username = username
                self.tags = tags
                self.settings = settings

        def load(self):
            pass

        def save(self):
            pass

    # Stores a list of data of groups.
    class Groups:
        items = None

        class Group:
            title = None
            description = None
            realm = None
            rules = None
            tags = None

            def __init__(self, title, description=None, realm=None, rules=None, tags=None):
                self.title = title
                self.description = description
                self.realm = realm
                self.rules = rules
                self.tags = tags

        def load(self):
            pass

        def save(self):
            pass


# Defines the structure of the Messages objects.
class Message:
    id = None
    sender = None
    receiver = None
    content = None
    type = None
    date = None
    reply = None
    markup = None

    def __init__(self, id, sender, receiver, content, type='text', date=None, reply=None, markup=None):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.type = type
        self.date = date
        self.reply = reply
        self.markup = markup
