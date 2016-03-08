from core.types import *
from queue import Queue

bot = Bot()

config = ConfigStore.Config
users = ConfigStore.Users
groups = ConfigStore.Groups
lang = ConfigStore.Language
tags = ConfigStore.Tags

plugins = list()

inbox = Queue()
outbox = Queue()
