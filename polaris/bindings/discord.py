import json
import logging
from multiprocessing import Process
from time import mktime, time

import html2markdown

import discord
from polaris.types import Conversation, Message, User
from polaris.utils import (catch_exception, download, is_int, send_request,
                           set_data, split_large_message)


class bindings(object):
    def __init__(self, bot):
        self.bot = bot
        self.custom_sender = True
        self.client = discord.Client()

    def get_me(self):
        return User(0, self.bot.name, None, self.bot.name)
        # return User(self.client.user.id, self.client.user.name, self.client.user.discriminator, self.client.user.name + '#' + self.client.user.discriminator, self.client.user.bot)

    def convert_message(self, msg):
        try:
            # logging.info(msg)
            id = msg.id
            extra = {}
            content = msg.content
            type = 'text'
            date = time()
            logging.info('%s - %s' %
                         (time(), mktime(msg.created_at.timetuple())))
            reply = None

            sender = User(msg.author.id, msg.author.name, msg.author.discriminator,
                          msg.author.name + '#' + msg.author.discriminator, msg.author.bot)

            conversation = Conversation(msg.channel.id)

            if hasattr(msg.channel, 'name'):
                conversation.title = msg.channel.name

            elif hasattr(msg.channel, 'recipient'):
                conversation.title = msg.channel.recipient.name

            return Message(id, conversation, sender, content, type, date, reply, extra)

        except Exception as e:
            logging.error(e)
            catch_exception(e, self.bot)

    def convert_inline(self, msg):
        pass

    def start_receiver(self):
        job = Process(target=self.receiver_worker, name='%s R.' % self.name)
        job.daemon = True
        job.start()

    def receiver_worker(self):
        logging.debug('Starting receiver worker...')

        @self.client.event
        async def on_ready():
            self.bot.info = User(self.client.user.id, self.client.user.name, self.client.user.discriminator,
                                 self.client.user.name + '#' + self.client.user.discriminator, self.client.user.bot)
            status = '%sstart' % self.bot.config.prefix
            activity = discord.Activity(
                type=discord.ActivityType.listening, name=status)
            await self.client.change_presence(activity=activity)

        @self.client.event
        async def on_message(message):
            # don't respond to ourselves
            if message.author.id == self.bot.info.id:
                return

            msg = self.convert_message(message)

            try:
                logging.info(
                    '[%s] %s@%s [%s] sent [%s] %s' % (msg.sender.id, msg.sender.first_name, msg.conversation.title, msg.conversation.id, msg.type, msg.content))
            except AttributeError:
                logging.info(
                    '[%s] %s@%s [%s] sent [%s] %s' % (msg.sender.id, msg.sender.title, msg.conversation.title, msg.conversation.id, msg.type, msg.content))
            try:
                self.bot.on_message_receive(msg)
                while self.bot.outbox.qsize() > 0:
                    msg = self.bot.outbox.get()
                    logging.info(' [%s] %s@%s [%s] sent [%s] %s' % (msg.sender.id, msg.sender.first_name,
                                                                    msg.conversation.title, msg.conversation.id, msg.type, msg.content))
                    await self.send_message(msg)

            except KeyboardInterrupt:
                pass

            except Exception as e:
                logging.error(e)
                if self.bot.started:
                    catch_exception(e, self.bot)

        self.client.run(self.bot.config['bindings_token'])

    async def send_message(self, message):
        try:
            channel = self.client.get_channel(message.conversation.id)
            if channel:
                content = message.content
                if message.extra and 'format' in message.extra:
                    if message.extra['format'] == 'HTML':
                        content = html2markdown.convert(content)

                if len(content) > 2000:
                    texts = split_large_message(content, 2000)
                    for text in texts:
                        await channel.send(text)

                else:
                    await channel.send(content)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            logging.error(e)
            if self.bot.started:
                catch_exception(e, self.bot)

    def get_input_file(self, content):
        return False

    def send_chat_action(self, conversation_id, type):
        return False

    def cancel_send_chat_action(self, conversation_id):
        return False

    # THESE METHODS DO DIRECT ACTIONS #
    def get_message(self, chat_id, message_id):
        return False

    def get_file(self, file_id, link=False):
        return False

    def join_by_invite_link(self, invite_link):
        return False

    def invite_conversation_member(self, conversation_id, user_id):
        return False

    def promote_conversation_member(self, conversation_id, user_id):
        return False

    def kick_conversation_member(self, conversation_id, user_id):
        return False

    def unban_conversation_member(self, conversation_id, user_id):
        return False

    def conversation_info(self, conversation_id):
        return False

    def get_chat_administrators(self, conversation_id):
        admins = []
        return admins
