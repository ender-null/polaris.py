import json
import logging
import os
from time import time

from DictObject import DictObject


class User(object):
    def __init__(self, id, first_name=None, last_name=None, username=None, is_bot=False, extra=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.is_bot = is_bot
        self.extra = extra

    def __str__(self):
        return '{} {} [{}]'.format(self.first_name, self.last_name, self.id)


class Conversation(object):
    def __init__(self, id, title=None, extra=None):
        self.id = id
        self.title = title
        self.extra = extra

    def __str__(self):
        return '{} [{}]'.format(self.title, self.id)


class Message(object):
    def __init__(self, id, conversation, sender, content, type='text', date=time(), reply=None, extra=None):
        self.id = id
        self.conversation = conversation
        self.sender = sender
        self.content = content
        self.type = type
        self.date = date
        self.reply = reply
        self.extra = extra

    def __str__(self):
        return '[{}] {}'.format(self.type, self.content)


# Thanks to luckydonald for this class ;) #
class AutosaveDict(DictObject):
    _database_file = None
    _autosafe = True

    def __init__(self, file, *args, autosafe=True, path=None, load_now=True, defaults=None, **kwargs):
        if path:
            file = os.path.join(path, file)
        super(AutosaveDict, self).__init__(*args, **kwargs)
        if defaults:
            if isinstance(defaults, dict):
                self.merge_dict(defaults)
            else:
                raise TypeError("Given default is not a dict subclass.")
        self._database_file = file
        self._autosafe = autosafe
        if load_now:
            try:
                self.load_database(merge=True)
            except (ValueError, TypeError, Exception):
                raise

    def after_set(self, key, value_to_set):
        if self._autosafe:
            self.store_database()

    @staticmethod
    def _parse_object(instance):
        if hasattr(instance, "as_dict"):
            return instance.as_dict()
        else:
            return instance

    def store_database(self):
        logging.debug("Saving AutosaveDict to {path}.".format(path=self._database_file))
        json_string = json.dumps(self, sort_keys=True, indent=4, separators=(',', ': '),
                                 default=self._parse_object)  # self still is a dict.
        if not os.path.exists(os.path.dirname(self._database_file)):
            os.makedirs(os.path.dirname(self._database_file))
        with open(self._database_file, "w+") as file:  # TODO: create folder.
            file.write(json_string)
            file.flush()
        logging.debug("Saved AutosaveDict to {path}".format(path=self._database_file))

    def enable_autosave(self, boolean=True):
        self._autosafe = boolean

    def load_database(self, merge=False):
        logging.debug("Loading database from {file}.".format(file=self._database_file))
        try:
            with open(self._database_file, "r", encoding='utf8') as file:
                json_data = file.read()
        except FileNotFoundError:
            logging.warning("File {file!r} was not found! Not loading anything!".format(file=self._database_file))
            return
        except Exception as e:
            logging.exception("Exception in loading file:")
            raise
        data = json.loads(json_data)
        if not merge:
            logging.debug("Not merging.")
            self._attribute_to_key_map.clear()
            self.clear()
            DictObject.__init__(self, data)
        else:
            logging.debug("Merging data.")
            self.merge_dict(data)
