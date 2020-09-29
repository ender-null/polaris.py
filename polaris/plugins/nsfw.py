import logging
from random import randint

from polaris.utils import generate_command_help, get_input, has_tag


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.nsfw.commands
        self.invalid_ids = []

    # Plugin action #
    def run(self, m):
        if has_tag(self.bot, m.conversation.id, 'nonsfw'):
            return self.bot.send_message(
                m, self.bot.trans.plugins.config.strings.disabled, extra={'format': 'HTML'})

        cid = '-1001230470587'

        if self.bot.info.is_bot:
            info = self.bot.conversation_info(cid)

            if info:
                msg = None
                last = info['last_message']['id']
                start = 1
                retries = 100

                while not msg:
                    rid = randint(start, last)
                    while rid in self.invalid_ids:
                        rid = randint(start, last)
                    msg = self.bot.get_message(cid, rid)
                    if not msg and not rid in self.invalid_ids:
                        retries -= 1
                        self.invalid_ids.append(rid)

                    if retries <= 0:
                        msg = self.bot.get_message(cid, last)
                        return self.bot.forward_message(msg, m.conversation.id)

                return self.bot.forward_message(msg, m.conversation.id)

        else:
            history = self.bot.bindings.server_request('getChatHistory',  {
                'chat_id': int(cid),
                'from_message_id': 0,
                'offset': 0,
                'limit': 100
            })

            if history:
                msg = None
                while not msg:
                    index = randint(0, len(history['messages']) - 1)
                    msg = self.bot.get_message(
                        cid, history['messages'][index]['id'])

                return self.bot.forward_message(msg, m.conversation.id)
