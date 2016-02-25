from core.types import *
from queue import Queue

bot = Bot()

config = Config.Config
users = Config.Users
groups = Config.Groups
lang = Config.Language

plugins = list()

inbox = Queue()
outbox = Queue()

started = True