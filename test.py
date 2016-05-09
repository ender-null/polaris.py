import inspect
import json
from os.path import isfile as exists
from pprint import pprint
from DictObject import DictObject

class DataStore(object):
    store = DictObject()
    def get_my_name(self):
        ans = []
        frame = inspect.currentframe().f_back
        tmp = dict(list(frame.f_globals.items()) + list(frame.f_locals.items()))
        for k, var in tmp.items():
            if isinstance(var, self.__class__):
                if hash(self) == hash(var) and k is not 'self':
                    ans.append(k)
        return ans[0]

    def __getitem__(self, key):
        if key not in self.store.keys():
            raise Exception("'" + key + "'" + " is not a valid key")
        return dict.__getitem__(self.store,key)

    def __setitem__(self, key, value):
        if key not in self.store.keys():
            raise Exception("'" + key + "'" + " is not a valid key")
        dict.__setitem__(self.store,key,value)

    def load(self):
        file_name = 'data/%s.json' % self.get_my_name()
        if exists(file_name):
            with open(file_name) as f:
                self.store = json.load(f)

    def save(self):
        file_name = 'data/%s.json' % self.get_my_name()
        if self.store:
            with open(file_name) as f:
                json.dump(self.store, f)

    def print_it(self):
        if self.store:
            pprint(self.store)

config = DataStore()
config.load()
config.print_it()