import asyncio
import functools
import json
import logging
import re
from multiprocessing import Process
from time import mktime, time

from polaris.types import Conversation, Message, User
from polaris.utils import (catch_exception, download, get_extension,
                           html_to_discord_markdown, is_int, positive,
                           send_request, set_data, split_large_message)

import discord
from discord.embeds import Embed
from discord.file import File


class bindings(object):
    def __init__(self, bot):
        self.bot = bot
        self.custom_sender = True
        self.custom_cron = True

    def server_request(self, api_method, params=None):
        return None

    def get_me(self):
        return User(0, self.bot.name, None, self.bot.name)

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

            sender = User(msg.author.id, msg.author.name, '#' + msg.author.discriminator,
                          msg.author.name + '#' + msg.author.discriminator, msg.author.bot)

            conversation = Conversation(msg.channel.id)

            if hasattr(msg.channel, 'name'):
                conversation.id = -msg.channel.id
                conversation.title = msg.channel.name

            elif hasattr(msg.channel, 'recipient'):
                conversation.id = msg.channel.recipient.id
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
        try:
            self.discord_loop = asyncio.new_event_loop()
            self.client = discord.Client(loop=self.discord_loop)
            self.bg_task = self.discord_loop.create_task(self.cron_task())
        except Exception as e:
            logging.error(e)
            if self.bot.started:
                catch_exception(e, self.bot)

        @self.client.event
        async def on_ready():
            self.bot.info = User(self.client.user.id, self.client.user.name, self.client.user.discriminator,
                                 self.client.user.name + '#' + self.client.user.discriminator, self.client.user.bot)
            status = '{}help'.format(self.bot.config.prefix)
            activity = discord.Activity(
                type=discord.ActivityType.listening, name=status)
            await self.client.change_presence(activity=activity)

        async def on_member_join(self, member):
            guild = member.guild
            if guild.system_channel is not None:
                sender = User(member.id, member.name, '#' + member.discriminator,
                          member.name + '#' + member.discriminator, member.bot)
                conversation = Conversation(guild.system_channel.id, guild.system_channel.name)
                extra = {
                    'user': sender
                }

                self.bot.outbox.put(Message(0, conversation, sender, 'new_chat_member', 'notification', time(), None, extra))

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
                if msg.content.startswith('/') or msg.content.startswith(self.bot.config.prefix):
                    if int(msg.conversation.id) > 0:
                        chat = self.client.get_user(msg.conversation.id)
                    else:
                        chat = self.client.get_channel(positive(msg.conversation.id))
                    await chat.trigger_typing()
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

        try:
            self.client.run(self.bot.config['bindings_token'])

        except KeyboardInterrupt:
            pass

        except Exception as e:
            logging.error(e)
            if self.bot.started:
                catch_exception(e, self.bot)

    async def cron_task(self):
        await self.wait_until_ready()

        while not self.is_closed() and self.started:
            for plugin in self.plugins:
                try:
                    if hasattr(plugin, 'cron'):
                        plugin.cron()

                except KeyboardInterrupt:
                    pass
                except Exception as e:
                    catch_exception(e, self)
            await asyncio.sleep(5)

        logging.info('is closed')

    async def send_message(self, message):
        try:
            if int(message.conversation.id) > 0:
                chat = self.client.get_user(message.conversation.id)
            else:
                chat = self.client.get_channel(positive(message.conversation.id))
            await chat.trigger_typing()
            if message.type == 'text':
                content = self.add_discord_mentions(chat, message.content)
                if message.extra:
                    if 'format' in message.extra and message.extra['format'] == 'HTML':
                        content = html_to_discord_markdown(content)
                    if 'preview' in message.extra and not message.extra['preview']:
                        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r'<\g<0>>', content, flags=re.MULTILINE)

                if len(content) > 2000:
                    texts = split_large_message(content, 2000)
                    for text in texts:
                        await chat.send(text)

                else:
                    await chat.send(content)

            elif message.type == 'photo' or message.type == 'document' or message.type == 'video' or message.type == 'voice':
                send_content = True
                embed = Embed()

                if message.extra and 'caption' in message.extra and message.extra['caption']:
                    lines = message.extra['caption'].split('\n')
                    embed.title = lines[0]
                    embed.description = '\n'.join(lines[1:])
                    send_content = False

                if send_content:
                    if message.content.startswith('/'):
                        await chat.send(file=discord.File(message.content, filename=message.type + get_extension(message.content)))
                    else:
                        await chat.send(message.content)

                else:
                    if message.content.startswith('/'):
                        await chat.send(file=discord.File(message.content, filename=message.type + get_extension(message.content)), embed=embed)
                    elif message.content.startswith('http'):
                        if message.type == 'photo':
                            embed.set_image(url=message.content)
                        elif message.type == 'video':
                            embed.set_video(url=message.content)
                        else:
                            embed.url = message.content
                        await chat.send(embed=embed)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            logging.error(e)
            if self.bot.started:
                catch_exception(e, self.bot)

    def add_discord_mentions(self, chat, content):
        matches = re.compile(r'(\@.[^\@]+\#[\d]+)').findall(content)
        if matches:
            for match in matches:
                if type(chat).__name__ == 'User':
                    user = chat
                else:
                    user = discord.utils.get(chat.guild.members, name=match.split('#')[0][1:], discriminator=match.split('#')[1])
                if user:
                    content = re.sub(match, f'{user.mention}', content, flags=re.MULTILINE)
        return content

    def get_input_file(self, content):
        return False


    # THESE METHODS DO DIRECT ACTIONS #
    def get_message(self, chat_id, message_id):
        channel = self.client.get_channel(positive(chat_id))
        message = self.discord_loop.create_task(channel.fetch_message(message_id))
        return self.convert_message(message)

    def get_file(self, file_id, link=False):
        return False

    def join_by_invite_link(self, invite_link):
        return False

    def invite_conversation_member(self, conversation_id, user_id):
        return False

    def promote_conversation_member(self, conversation_id, user_id):
        return False

    def kick_conversation_member(self, conversation_id, user_id):
        if int(conversation_id) > 0:
            return False
        channel = self.client.get_channel(positive(conversation_id))
        user = self.client.get_user(user_id)
        try:
            self.discord_loop.create_task(channel.guild.kick(user))
            return True
        except:
            return False

    def unban_conversation_member(self, conversation_id, user_id):
        return False

    def conversation_info(self, conversation_id):
        return False

    def get_chat_administrators(self, conversation_id):
        if int(conversation_id) > 0:
            return False
        channel = self.client.get_channel(positive(conversation_id))
        admins = []
        for member in channel.members:
            perms = channel.permissions_for(member)
            if perms.administrator:
                admins.append(User(member.id, member.name, '#' + member.discriminator, member.name + '#' + member.discriminator, member.bot))
        logging.info(admins)
        return admins

    def create_webhook(self, channel_id, name, avatar=None):
        def create_webhook_request(avatar):
            channel = self.client.get_channel(positive(channel_id))
            if channel and channel.guild:
                webhook = self.discord_loop.create_task(channel.create_webhook(name=name,avatar=avatar))
            else:
                logging.info('invalid channel')

        if not avatar:
            avatar = self.discord_loop.create_task(self.client.user.avatar_url.read())
            avatar.add_done_callback(lambda t: create_webhook_request(t.result()))
