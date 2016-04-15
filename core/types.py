from core.shared import *
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
    type = 'private'

    def __init__(self, id=None, first_name=None, last_name=None, username=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


# Defines the structure of the Group objects.
class Group:
    id = None
    title = None
    type = None

    def __init__(self, id=None, title=None, type='group'):
        self.id = id
        self.title = title
        self.type = type


class DataStore(DictObject):
    def __init__(self):
        for key in self.keys():
            self[key] = None

    def __getitem__(self, key):
        if key not in self.keys():
            raise Exception("'" + key + "'" + " is not a valid key")
        return dict.__getitem__(self,key)

    def __setitem__(self, key, value):
        if key not in self.keys():
            raise Exception("'" + key + "'" + " is not a valid key")
        dict.__setitem__(self,key,value)
        
    def load(self):
        try:
            with open('data/%s' % type(self).__name__, 'r') as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
                for key in data:
                    self[key] = None
                return True
        except:
            raise Exception('[Failed] %s.json NOT loaded.' % type(self).__name__)

    def save(self):
        try:
            with open('data/%s' % type(self).__name__, 'w') as f:
                json.dump(self, f, sort_keys=True, indent=4)
                return True
        except:
            raise Exception('[Failed] %s.json NOT saved.' % type(self).__name__)
        
        
# This classes define and manage configuration files and stored data.
class ConfigStore:
    # Main configuration file.
    class Config:
        wrapper = None
        owner = None
        keys = None
        plugins = []
        timeout = 10
        start = '/'
        language = 'default'

        def load(self):
            try:
                with open('data/config.json', 'r') as f:
                    data = DictObject(json.load(f, object_pairs_hook=OrderedDict))
                    
                    self.wrapper = data.wrapper
                    self.owner = data.owner
                    self.keys = DictObject(data['keys'])
                    self.plugins = data.plugins
                    self.timeout = data.timeout
                    self.start = data.start
                    self.language = data.language
                    print('\t%s[OK] config.json loaded.%s' % (Colors.OKGREEN, Colors.ENDC))
            except:
                self.keys = DictObject()
                print('\t%s[Failed] config.json NOT loaded.%s' % (Colors.FAIL, Colors.ENDC))

        def save(self):
            try:
                with open('data/config.json', 'w') as f:

                    config_tuples = [
                        ('wrapper', self.wrapper),
                        ('owner', self.owner),
                        ('keys', self.keys),
                        ('plugins', sorted(self.plugins)),
                        ('timeout', self.timeout),
                        ('start', self.start),
                        ('language', self.language)
                    ]
                    
                    config = OrderedDict(config_tuples)

                    json.dump(config, f, sort_keys=True, indent=4)
                    print('\t%s[OK] config.json saved.%s' % (Colors.OKGREEN, Colors.ENDC))
            except:
                print('\t%s[Failed] config.json NOT saved.%s' % (Colors.FAIL, Colors.ENDC))

    # Defines a language for the messages.
    class Language:
        messages = None
        errors = None
        interactions = None

        def load(self):
            try:
                file = config.language
            except NameError:
                file = 'default'

            try:
                with open('lang/%s.json' % file, 'r') as f:
                    data = DictObject(json.load(f, object_pairs_hook=OrderedDict))
                    self.messages = data.messages
                    self.errors = data.errors
                    self.interactions = data.interactions
                    print('\t%s[OK] %s.json loaded.%s' % (Colors.OKGREEN, file, Colors.ENDC))
            except:
                self.messages = DictObject()
                self.errors = DictObject()
                self.interactions = DictObject()
                print('\t%s[Failed] %s.json NOT loaded.%s' % (Colors.FAIL, file, Colors.ENDC))

        def save(self):
            try:
                file = config.language
            except NameError:
                file = 'default'

            try:
                with open('lang/%s.json' % file, 'w') as f:

                    config_tuples = [
                        ('messages', self.messages),
                        ('errors', self.errors),
                        ('interactions', self.interactions)
                    ]

                    config = OrderedDict(config_tuples)

                    json.dump(config, f, sort_keys=True, indent=4)
                    print('\t%s[OK] %s.json saved.%s' % (Colors.OKGREEN, file, Colors.ENDC))
            except:
                print('\t%s[Failed] %s.json NOT saved.%s' % (Colors.FAIL, file, Colors.ENDC))

    # Stores a list of data of users.
    class Users:
        items = None

        class User:
            first_name = None
            last_name = None
            username = None
            settings = None

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

        def load(self):
            pass

        def save(self):
            pass

    class Tags:
        list = None

        def load(self):
            try:
                with open('data/tags.json', 'r') as f:
                    data = json.load(f, object_pairs_hook=OrderedDict)
                    self.list = DictObject(data)

                    print('\t%s[OK] tags.json loaded.%s' % (Colors.OKGREEN, Colors.ENDC))
            except:
                self.list = DictObject()
                print('\t%s[Failed] tags.json NOT loaded.%s' % (Colors.FAIL, Colors.ENDC))

        def save(self):
            try:
                with open('data/tags.json', 'w') as f:
                    json.dump(self.list, f, sort_keys=True, indent=4)
                    print('\t%s[OK] tags.json saved.%s' % (Colors.OKGREEN, Colors.ENDC))
            except:
                print('\t%s[Failed] tags.json NOT saved.%s' % (Colors.FAIL, Colors.ENDC))


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

    def __init__(self, id=None, sender=None, receiver=None, content=None, type='text', date=None, reply=None, markup=None, extra=None):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.type = type
        self.date = date
        self.reply = reply
        self.markup = markup
        self.extra = extra

class PolarisExceptions():       
    class FailedException(Exception):
        pass
    
    class NotAdminException(Exception):
        pass

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
