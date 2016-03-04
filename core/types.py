from collections import OrderedDict
from DictObject import DictObject
import json, importlib


# Used to store the bindings module and the User data of the bot.
class Bot:
    id = None
    first_name = None
    last_name = None
    username = None
    wrapper = None
    inbox_listener = None
    outbox_listener = None
    started = None
        
    def start(self):
        self.started = True
        self.inbox_listener.start()
        self.outbox_listener.start()

    def set_wrapper(self, wrapper='api'):
        self.wrapper = importlib.import_module('core.wrapper.' + wrapper)


# Defines the structure of the User objects.
class User:
    id = None
    first_name = None
    last_name = None
    username = None

    def __init__(self, id=None, first_name=None, last_name=None, username=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


# Defines the structure of the Group objects.
class Group:
    id = None
    title = None

    def __init__(self, id=None, title=None):
        self.id = id
        self.title = title


# This classes define and manage configuration files and stored data.
class Config:
    # Main configuration file.
    class Config:
        wrapper = None
        owner = None
        keys = None
        plugins = []
        chats = []
        start = '/'

        def load(self):
            try:
                with open('data/config.json', 'r') as f:
                    config_json = json.load(f, object_pairs_hook=OrderedDict)

                    self.wrapper = config_json['wrapper']
                    self.owner = config_json['owner']
                    self.keys = DictObject(config_json['keys'])
                    self.plugins = config_json['plugins']
                    self.chats = config_json['chats']
                    self.start = config_json['start']
                    print('\t[OK] config.json loaded.')
            except:
                self.keys = DictObject()
                print('\t%s[Failed] config.json NOT loaded.%s' % (Colors.FAIL, Colors.ENDC))

        def save(self):
            try:
                with open('data/config.json', 'w') as f:

                    config_tuples = (
                        ('wrapper', self.wrapper),
                        ('owner', self.owner),
                        ('keys', self.keys),
                        ('plugins', self.plugins),
                        ('chats', self.chats),
                        ('start', self.start)
                    )

                    config = OrderedDict(config_tuples)

                    json.dump(config, f, sort_keys=True, indent=4)
                    print('\t[OK] config.json saved.')
            except:
                print('\t%s[Failed] config.json NOT saved.%s' % (Colors.FAIL, Colors.ENDC))

    # Defines a language for the messages.
    class Language:
        message = DictObject()
        error = DictObject()
        plugins = DictObject()

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
    extra = None

    def __init__(self, id, sender, receiver, content, type='text', date=None, reply=None, markup=None, extra=None):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.type = type
        self.date = date
        self.reply = reply
        self.markup = markup
        self.extra = extra


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
