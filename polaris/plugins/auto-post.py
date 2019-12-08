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
        if datetime.now().minute == 0 and datetime.now().second < 8:
            # self.bot.tags = wait_until_received('tags/' + self.bot.name)

            topics = ['bdsm']

            for topic in topics:
                self.send_random_message_to_conversation(topic)

    def send_random_message_to_conversation(self, topic = '?'):
        try:
            if hasattr(self.bot.trans.plugins, 'autopost'):
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
            for cid in self.bot.tags:
                if has_tag(self.bot, cid, 'autopost:' + topic) or has_tag(self.bot, cid, 'autopost'):
                    conversations.append(cid)

        return conversations
