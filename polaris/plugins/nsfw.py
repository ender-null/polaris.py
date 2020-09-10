import logging
from random import randint

from polaris.utils import generate_command_help, get_input, has_tag


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.nsfw.commands

    # Plugin action #
    def run(self, m):
        if has_tag(self.bot, m.conversation.id, 'nonsfw'):
            return self.bot.send_message(
                m, self.bot.trans.plugins.config.strings.disabled, extra={'format': 'HTML'})

        cid = '-1001003803132'  # '-1001339508722'
        tags = has_tag(self.bot, cid, 'media:?', return_match=True)
        if tags:
            for tag in tags:
                if 'media' in tag:
                    count = int(tag.split(':')[1])
                    msg = None
                    while not msg:
                        random = randint(0, count)
                        msg = self.bot.get_message(cid, random)

                    self.bot.forward_message(msg, m.conversation.id)
