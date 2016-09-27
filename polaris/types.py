from polaris import utils
from DictObject import DictObject
from time import time
import json, collections, logging

class User(object):
    def __init__(self, id, first_name = None, last_name = None, username = None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    def __str__(self):
        return self.id

class Conversation(object):
    def __init__(self, id, title = None):
        self.id = id
        self.title = title

    def __str__(self):
        return self.id

class Message(object):
    def __init__(self, id, conversation, sender, content, type, date = time(), reply = None, extra = None):
        self.id = id
        self.conversation = conversation
        self.sender = sender
        self.content = content
        self.type = type
        self.date = date
        self.reply = reply
        self.extra = extra

    def __str__(self):
        return self.content

class json2obj(object):
    def __init__(self, string):
        if isinstance(string, str):
            self.json = json.loads(string)
        else:
            self.json = string

        if('from' in self.json):
            self.json['_from_'] = self.json.pop('from')
        for x in self.json:
            class_ = self.json[x].__class__ if isinstance(self.json, dict) else x.__class__
            if(self.json.__class__ == list):
                if(x.__class__.__name__ in ['list', 'dict']):
                    i = self.json.index(x)
                    self.json[i] = json2obj(json.dumps(self.json[i]))
            if(self.json.__class__ == dict):
                if(self.json[x].__class__.__name__ in ['list', 'dict']):
                    self.json[x] = json2obj(json.dumps(self.json[x]))
        if(self.json.__class__ != list):
            self.__dict__.update(self.json)
    
    def __getattr__(self, attr):
        return False

    def __iter__(self):
        return iter(self.json)

    def __len__(self):
        return len(self.json)

class json2file(json2obj):
    def __init__(self, path):
        self.path = path
        try:
            self.load()
            super().__init__(self.data)
        except Exception as e:
            logging.error(e)

    def save(self):
        try:
            with open(self.path, 'w') as file:
                json.dump(self.data, file, sort_keys = True, indent = 4)
                logging.info('Saved succesfully: %s' % self.path)
        except:
            logging.error('Failed saving: %s' % self.path)
        pass

    def load(self):
        try:
            with open(self.path, 'r') as file:
                self.data = json.load(file)
                logging.info('Loaded succesfully: %s' % self.path)
        except:
            logging.error('Failed loading: %s' % self.path)
