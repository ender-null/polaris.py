from polaris.types import AutosaveDict, Message, Conversation
from polaris.utils import set_logger, is_int, load_plugin_list, get_step, cancel_steps, get_plugin_name, init_if_empty, catch_exception, wait_until_received, has_tag, set_input
from multiprocessing import Process, Queue
from threading import Thread
from time import sleep, time
from firebase_admin import db
import importlib, logging, re, traceback, sys, os, json, signal


class Bot(object):
    def __init__(self, name):
        self.name = name
        self.get_database()
        self.bindings = importlib.import_module('polaris.bindings.%s' % self.config['bindings']).bindings(self)
        self.inbox = Queue()
        self.outbox = Queue()
        self.started = False
        self.plugins = None
        self.jobs = None
        self.info = self.bindings.get_me()

        if self.info is None:
            raise Exception

    def get_database(self):
        try:
            self.config = wait_until_received('bots/' + self.name)
            self.trans = wait_until_received('translations/' + self.config['translation'])
            self.users = wait_until_received('users/' + self.name)
            self.groups = wait_until_received('groups/' + self.name)
            self.steps = wait_until_received('steps/' + self.name)
            self.tags = wait_until_received('tags/' + self.name)
            self.settings = wait_until_received('settings/' + self.name)
            self.administration = wait_until_received('administration/' + self.name)
            self.pins = wait_until_received('pins/' + self.name)
            self.reminders = wait_until_received('reminders/' + self.name)
            self.poles = wait_until_received('poles/' + self.name)
        except Exception as e:
            catch_exception(e, self)


    def sender_worker(self):
        try:
            logging.debug('Starting sender worker...')
            while self.started:
                msg = self.outbox.get()
                logging.info(' %s@%s sent [%s] %s' % (msg.sender.first_name, msg.conversation.title, msg.type, msg.content))
                self.bindings.send_message(msg)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            catch_exception(e, self)


    def messages_handler(self):
        try:
            logging.debug('Starting message handler...')
            while self.started:
                msg = self.inbox.get()
                try:
                    logging.info('%s@%s sent [%s] %s' % (msg.sender.first_name, msg.conversation.title, msg.type, msg.content))
                except AttributeError:
                    logging.info('%s@%s sent [%s] %s' % (msg.sender.title, msg.conversation.title, msg.type, msg.content))

                self.on_message_receive(msg)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            catch_exception(e, self)


    def start(self):
        if not 'enabled' in self.config or self.config.enabled:
            if self.started:
                self.stop()

            self.started = True
            self.plugins = self.init_plugins()

            logging.info('Connected as %s (@%s)' % (self.info.first_name, self.info.username))

            self.jobs = []
            self.jobs.append(Process(target=self.bindings.receiver_worker, name='%s R.' % self.name))
            self.jobs.append(Process(target=self.sender_worker, name='%s S.' % self.name))
            self.jobs.append(Process(target=self.cron_jobs, name='%s C.' % self.name))
            self.jobs.append(Process(target=self.messages_handler, name='%s' % self.name))

            for job in self.jobs:
                #if job.name != self.name:
                job.daemon = True
                job.start()

        else:
            logging.info('[%s] is not enabled!' % self.name)

    def stop(self):
        self.started = False
        for job in self.jobs:
            # if job.daemon:
            logging.info('Terminating process [%s] with PID %s' % (job.name, job.pid))
            os.kill(job.pid, signal.SIGKILL)


    def init_plugins(self):
        plugins = []

        logging.debug('Importing plugins...')

        if type(self.config.plugins) is list:
            plugins_to_load = self.config.plugins
        elif self.config.plugins == 'all':
            plugins_to_load = load_plugin_list()
        else:
            plugins_to_load = load_plugin_list()

        for plugin in plugins_to_load:
            try:
                plugins.append(importlib.import_module('polaris.plugins.' + plugin).plugin(self))
                logging.debug('  [OK] %s ' % (plugin))
            except Exception as e:
                logging.error('  [Failed] %s - %s ' % (plugin, str(e)))

        logging.debug('  Loaded: ' + str(len(plugins)) + '/' + str(len(plugins_to_load)))

        return plugins


    def on_message_receive(self, msg):
        try:
            if msg.content == None or (msg.type != 'inline_query' and msg.date < time() - 60):
                return

            if msg.sender.id != self.config['owner'] and (has_tag(self, msg.conversation.id, 'muted') or has_tag(self, msg.sender.id, 'muted')):
                return

            step = get_step(self, msg.conversation.id)

            if step:
                for plugin in self.plugins:
                    if get_plugin_name(plugin) == step.plugin and hasattr(plugin, 'steps'):
                        if msg.content.startswith('/cancel'):
                            plugin.steps(msg, -1)
                            cancel_steps(self, msg.conversation.id)

                        if msg.content.startswith('/done'):
                            plugin.steps(msg, 0)
                            cancel_steps(self, msg.conversation.id)

                        else:
                            plugin.steps(msg, step['step'])

            else:
                for plugin in self.plugins:
                    # Always do this action for every message. #
                    if hasattr(plugin, 'always'):
                        plugin.always(msg)

                    # If no query show help #
                    if msg.type == 'inline_query':
                        if msg.content == '':
                            msg.content = 'help'

                    # Check if any command of a plugin matches. #
                    for command in plugin.commands:
                        if 'parameters' not in command:
                            command['parameters'] = None

                        if 'command' in command:
                            if self.check_trigger(command['command'], command['parameters'], msg, plugin):
                                break

                        if 'friendly' in command:
                            if self.check_trigger(command['friendly'], command['parameters'], msg, plugin, True):
                                break

                        if 'shortcut' in command:
                            if self.check_trigger(command['shortcut'], command['parameters'], msg, plugin):
                                break

        except KeyboardInterrupt:
            pass

        except Exception as e:
            catch_exception(e, self)


    def check_trigger(self, command, parameters, message, plugin, friendly = False):
        if isinstance(command, str):
            command = command.lower()
            if isinstance(message.content, str) and message.content.endswith('@' + self.info.username) and ' ' not in message.content:
                message.content = message.content.replace('@' + self.info.username, '')

            # If the commands are not /start or /help, set the correct command start symbol. #
            if ((command == '/start' and '/start' in message.content) or
               (command == '/help' and '/help' in message.content)):
                trigger = command.replace('/', '^/')
            else:
                if message.type == 'inline_query':
                    trigger = command.replace('/', '^')
                else:
                    trigger = command.replace('/', '^' + self.config.prefix)

                if not friendly:
                    # trigger = trigger.replace('@' + self.info.username.lower(), '')
                    if not parameters and trigger.startswith('^'):
                        trigger += '$'
                    elif parameters and ' ' not in message.content and not message.reply:
                        trigger += '$'
                    elif parameters and ' ' in message.content:
                        trigger += ' '

            try:
                if message.content and isinstance(message.content, str) and re.compile(trigger, flags=re.IGNORECASE).search(message.content):
                    set_input(message, trigger)

                    if message.type == 'inline_query':
                        if hasattr(plugin, 'inline'):
                            plugin.inline(message)

                    else:
                        plugin.run(message)

                    return True
            except Exception as e:
                catch_exception(e, self)
                self.send_message(message, self.trans.errors.exception_found, extra={'format': 'HTML'})
                return False
        return False


    def cron_jobs(self):
        while(self.started):
            for plugin in self.plugins:
                try:
                    if hasattr(plugin, 'cron'):
                        plugin.cron()

                except KeyboardInterrupt:
                    pass
                except Exception as e:
                    catch_exception(e, self)
            sleep(5)


    # METHODS TO MANAGE MESSAGES #
    def send_message(self, msg, content, type='text', reply=None, extra=None):
        message = Message(None, msg.conversation, self.info, content, type, reply=reply, extra=extra)
        self.outbox.put(message)


    def forward_message(self, msg, id):
        self.outbox.put(Message(None, msg.conversation, self.info, msg.content, 'forward',
                                extra={"message": msg.id, "conversation": id}))

    def answer_inline_query(self, msg, results, extra = {}):
        self.outbox.put(Message(msg.id, msg.conversation, self.info, json.dumps(results), 'inline_results', extra))


    # THESE METHODS DO DIRECT ACTIONS #
    def get_file(self, file_id):
        return self.bindings.get_file(file_id)


    def invite_user(self, msg, user_id):
        return self.bindings.invite_conversation_member(msg.conversation.id, user_id)


    def kick_user(self, msg, user_id):
        return self.bindings.kick_conversation_member(msg.conversation.id, user_id)


    def unban_user(self, msg, user_id):
        return self.bindings.unban_conversation_member(msg.conversation.id, user_id)


    def conversation_info(self, conversation_id):
        return self.bindings.conversation_info(conversation_id)


    def send_alert(self, text):
        message = Message(None, Conversation(self.config.alerts_conversation_id, 'Alerts'), self.info, '<pre>%s</pre>' % text, extra={'format': 'HTML', 'preview': False})
        self.outbox.put(message)
