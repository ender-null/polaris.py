from polaris.types import Message, Conversation, User
from polaris.utils import send_request, catch_exception, set_data
from six import string_types
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
import logging, json


class bindings(object):
    def __init__(self, bot):
        self.bot = bot
        self.client = TelegramClient(StringSession(self.bot.config['bindings_token']), self.bot.config['api_keys']['telegram_app_id'], self.bot.config['api_keys']['telegram_api_hash']).start()
        self.clientSender = None
        self.clientReceiver = None


    def get_me(self):
        me = self.client.get_me()
        return User(me.id, me.first_name, me.last_name, me.username, me.bot)

    async def convert_message(self, msg):
        try:
            id = msg.id 
            raw_chat = await msg.get_chat()
            conversation = Conversation(int(raw_chat.id))
            if hasattr(raw_chat, 'title'):
                conversation.title = raw_chat.title
            else:
                conversation.title = raw_chat.first_name
            raw_sender = await msg.get_sender()
            sender = User(int(raw_sender.id))
            if hasattr(raw_sender, 'first_name'):
                sender.first_name = str(raw_sender.first_name)
            if hasattr(raw_sender, 'last_name'):
                sender.last_name = str(raw_sender.last_name)
            if hasattr(raw_sender, 'username'):
                sender.username = str(raw_sender.username)
            content = msg.text
            type = 'text'
            date = msg.date.timestamp()
            reply = None
            extra = {}
            return Message(id, conversation, sender, content, type, date, reply, extra)

        except Exception as e:
            catch_exception(e, self.bot)


    def convert_inline(self, msg):
        pass


    def receiver_worker(self):
        logging.debug('Starting receiver worker...')
        try:
            self.clientReceiver = TelegramClient(StringSession(self.bot.config['bindings_token']), self.bot.config['api_keys']['telegram_app_id'], self.bot.config['api_keys']['telegram_api_hash'])

            @self.clientReceiver.on(events.NewMessage)
            async def on_message_receive(msg):
                message = await self.convert_message(msg)
                self.bot.inbox.put(message)
                await self.clientReceiver.send_read_acknowledge(await msg.get_chat(), msg)
                set_data('bots/%s/bindings_token' % self.bot.name, StringSession.save(self.clientReceiver.session))

            self.clientReceiver.start()
            self.clientReceiver.run_until_disconnected()

        except KeyboardInterrupt:
            pass

        except Exception as e:
            if self.bot.started:
                catch_exception(e, self.bot)



    def send_message(self, message):
        try:
            if not self.clientSender:
                self.clientSender = TelegramClient(StringSession(self.bot.config['bindings_token']), self.bot.config['api_keys']['telegram_app_id'], self.bot.config['api_keys']['telegram_api_hash']).start()

            if message.type == 'text':
                if 'format' in message.extra and message.extra['format'] == 'Markdown':
                    self.clientSender.send_message(message.conversation.id, message.content, parse_mode = 'markdown')
                elif 'format' in message.extra and message.extra['format'] == 'HTML':
                    self.clientSender.send_message(message.conversation.id, message.content, parse_mode = 'html')
                else:
                    self.clientSender.send_message(message.conversation.id, message.content, parse_mode =  None)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            if self.bot.started:
                catch_exception(e, self.bot)


    # THESE METHODS DO DIRECT ACTIONS #
    def get_file(self, file_id):
        pass


    def invite_conversation_member(self, conversation_id, user_id):
        pass

    def kick_conversation_member(self, conversation_id, user_id):
        pass

    def unban_conversation_member(self, conversation_id, user_id):
        pass

    def conversation_info(self, conversation_id):
        pass

    def get_chat_administrators(self, conversation_id):
        pass