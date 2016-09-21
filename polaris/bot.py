from polaris import utils, types, loader
from polaris.types import json2file
from multiprocessing import Process, Queue
import importlib, logging, time, re

class Bot(object):
    def __init__(self, name):
        self.name = name
        self.config = json2file('bots/%s.json' % name)
        self.started = False
        self.inbox = Queue()
        self.outbox = Queue()
        self.connector = importlib.import_module('polaris.connectors.%s' % self.config.connector)
        self.plugins = loader.import_plugins(self.config.plugins)
        self.info = self.connector.get_me(self)

    def receiver_worker(self):
        try:
            logging.debug('Starting receiver worker...')
            while self.started:
                self.connector.get_messages(self)
        except KeyboardInterrupt:
            pass

    def sender_worker(self):
        try:
            logging.debug('Starting sender worker...')
            while self.started:
                msg = self.outbox.get()
                logging.info(' %s@%s sent [%s] %s' % (msg.sender.first_name, msg.conversation.title, msg.type, msg.content))
                self.connector.send_message(self, msg)
        except KeyboardInterrupt:
            pass

    def messages_handler(self):
        try:
            logging.debug('Starting message handler...')
            while self.started:
                msg = self.inbox.get()
                logging.info('%s@%s sent [%s] %s' % (msg.sender.first_name, msg.conversation.title, msg.type, msg.content))

                self.on_message_receive(msg)

        except KeyboardInterrupt:
            pass

    def start(self):
        self.started = True
        logging.debug('Connected as %s (@%s)' % (self.info.first_name, self.info.username))

        jobs = []
        jobs.append(Process(target=self.receiver_worker, name='%sReceiver' % self.name))
        jobs.append(Process(target=self.sender_worker, name='%sSender' % self.name))
        jobs.append(Process(target=self.messages_handler, name='%s' % self.name))

        for job in jobs:
            job.daemon = True
            job.start()


    def stop(self):
        self.started = False

    def on_message_receive(self, msg):
        for plugin in self.plugins:
            for command, parameters in plugin.commands.items():
                if msg.content:
                    self.check_trigger(command, msg, plugin)

    def check_trigger(self, command, message, plugin):
        trigger = command.replace('/', '^' + self.config.command_start)

        if message.type == 'inline_query':
            trigger = trigger.replace(self.config.command_start, '')

        if message.content and re.compile(trigger).search(message.content.lower()):
            try:
                if hasattr(plugin, 'inline') and message.type == 'inline_query':
                    return plugin.inline(self, message)
                else:
                    return plugin.run(self, message)
            except Exception as e:
                logging.error(e)



