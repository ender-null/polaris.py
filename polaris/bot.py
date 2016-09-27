from polaris import utils, types, loader
from polaris.types import json2file, Message
from multiprocessing import Process, Queue
import importlib, logging, time, re, traceback

class Bot(object):
    def __init__(self, name):
        self.name = name
        self.config = json2file('bots/%s.json' % self.name)
        self.lang = json2file('polaris/languages/%s.json' % self.config.language)
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

                p = Process(target=self.on_message_receive, args=(msg,), name='%s' % self.name)
                p.daemon = True
                p.start()

        except KeyboardInterrupt:
            pass

    def start(self):
        self.started = True
        logging.debug('Connected as %s (@%s)' % (self.info.first_name, self.info.username))

        jobs = []
        jobs.append(Process(target=self.receiver_worker, name='%sReceiver' % self.name))
        jobs.append(Process(target=self.sender_worker, name='%sSender' % self.name))
        # jobs.append(Process(target=self.messages_handler, name='%s' % self.name))
        
        for job in jobs:
            job.daemon = True
            job.start()

        Process(target=self.messages_handler, name='%s' % self.name).start()


    def stop(self):
        self.started = False

    def on_message_receive(self, msg):
        for plugin in self.plugins:
            for command, args in plugin.commands.items():
                if 'friendly' in args:
                    logging.debug('FRIENDLY: %s' % args['friendly'])
                    self.check_trigger(args['friendly'], msg, plugin)

                logging.debug('STANDARD: %s' % command)
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

    # METHODS TO MANAGE MESSAGES #
    def send_message(self, msg, text, reply = None, extra = None):
        self.outbox.put(Message(None, msg.conversation, self.info, text, 'text', reply=reply, extra=extra))

    def send_photo(self, msg, photo, reply = None, extra = None):
        self.outbox.put(Message(None, msg.conversation, self.info, photo, 'photo', reply=reply, extra=extra))

    def send_document(self, msg, document, reply = None, extra = None):
        self.outbox.put(Message(None, msg.conversation, self.info, document, 'document', reply=reply, extra=extra))

    def send_video(self, msg, document, reply = None, extra = None):
        self.outbox.put(Message(None, msg.conversation, self.info, video, 'video', reply=reply, extra=extra))

    def send_audio(self, msg, document, reply = None, extra = None):
        self.outbox.put(Message(None, msg.conversation, self.info, audio, 'audio', reply=reply, extra=extra))

    def send_voice(self, msg, document, reply = None, extra = None):
        self.outbox.put(Message(None, msg.conversation, self.info, voice, 'voice', reply=reply, extra=extra))

    def send_sticker(self, msg, sticker, reply = None, extra = None):
        self.outbox.put(Message(None, msg.conversation, self.info, sticker, 'sticker', reply=reply, extra=extra))

    def forward_message(self, msg, id):
        self.outbox.put(Message(None, msg.conversation, self.info, msg.content, 'forward', extra = {"message": msg.id, "conversation": id}))

    def answer_inline_query(self, msg, results, offset = None):
        self.outbox.put(Message(None, msg.conversation, self.info, results, 'inline_results', extra = {"offset": offset}))

    def get_file(self, file_id, only_url=False):
        try:
            return self.connector.get_file(file_id, only_url)
        except:
            return None


    def invite_user(self, msg, user):
        try:
            self.connector.invite_chat_member(m.receiver.id, user)
        except PermissionError:
            return None
        except Exception:
            return False
        else:
            return True


    def kick_user(self, msg, user):
        try:
            self.connector.kick_chat_member(m.receiver.id, user)
        except PermissionError:
            return None
        except Exception:
            return False
        else:
            return True
            

    def unban_user(self, msg, user):
        try:
            self.connector.unban_chat_member(m.receiver.id, user)
        except PermissionError:
            return None
        except Exception:
            return False
        else:
            return True


    def chat_info(self, chat):
        try:
            return self.connector.chat_info(chat)
        except:
            return chat

    def send_alert(self, text):
        for id in tags.list:
            if 'type:alerts' in tags.list[id]:
                text = '<code>%s</code>' % text
                
                if int(id) > 0:
                    receiver = User()
                    receiver.id = int(id)
                    receiver.first_name = id
                    message = Message(None, bot, receiver, text, markup='HTML')
                else:
                    receiver = Group()
                    receiver.id = int(id)
                    receiver.title = id
                    
                message = Message(None, bot, receiver, text, markup='HTML')
                outbox.put(message)
        
    def send_exception(self, msg, ):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)
        text = 'Traceback (most recent call last)'
        for row in tb:
            text += '\n\tFile "%s", line %s, in %s\n\t\t%s' % (row[0], row[1], row[2], row[3])
        if exc_type:
            text += '\n%s: %s' % (exc_type.__name__, exc_obj)
        
        if exc_type.__name__ == 'ReadTimeout':
            error = lang.errors.connection
        else:
            error = lang.errors.exception
            
        if m.receiver.id > 0:
            message = Message(None, m.receiver, m.sender, '%s' % error, 'text', extra=False, markup='HTML')
        else:
            message = Message(None, bot, m.receiver, '%s' % error, 'text', extra=False, markup='HTML')
        outbox.put(message)
        send_alert(text)
