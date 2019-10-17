from polaris.utils import has_tag, wait_until_received
from polaris.types import Message, Conversation
from random import randint
from datetime import datetime
import logging


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot

    def cron(self):
        if datetime.now().second < 6:
            self.bot.tags = wait_until_received('tags/' + self.bot.name)
            self.bot.users = wait_until_received('users/' + self.bot.name)
            self.bot.groups = wait_until_received('groups/' + self.bot.name)

        topics = ['bdsm']

        for topic in topics:
            self.send_random_message_to_conversation(topic)

    def send_random_message_to_conversation(self, topic = '?'):
        try:
            if hasattr(self.bot.trans.plugins, 'autopost'):
                if datetime.now().minute == 0 and datetime.now().second < 6:
                    strings = self.bot.trans.plugins.autopost.strings[topic]
                    i = randint(0, len(strings) - 1)
                    text = strings[i]
                    for cid in self.get_conversations_to_post(topic):
                        m = Message(None, Conversation(int(cid)), None, None)
                        self.bot.send_message(m, text, extra={'format': 'HTML'})

        except Exception as e:
            logging.info('Exception found: ' + str(e))

    def get_conversations_to_post(self, topic = '?'):
        conversations = []

        if self.bot.users:
            for uid in self.bot.users:
                if has_tag(self.bot, uid, 'autopost:' + topic) or has_tag(self.bot, uid, 'autopost'):
                    conversations.append(uid)

        if self.bot.groups:
            for gid in self.bot.groups:
                if has_tag(self.bot, gid, 'autopost:' + topic) or has_tag(self.bot, gid, 'autopost'):
                    conversations.append(gid)

        return conversations