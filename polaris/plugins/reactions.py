from polaris.utils import get_input, is_command, init_if_empty, wait_until_received, set_data, delete_data
from polaris.types import AutosaveDict
from firebase_admin import db
from firebase_admin.db import ApiCallError
from re import findall, compile, IGNORECASE

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.update_triggers()

    # Plugin action #
    def run(self, m):
        for reaction, attributes in self.bot.trans.plugins.reactions.strings.items():
            for trigger in attributes:
                if compile(trigger, flags=IGNORECASE).search(m.content):
                    return self.bot.send_message(m, reaction, extra={'format': 'HTML'})


    def update_triggers(self):
        self.commands = []

        # Add new triggers #
        for reaction, attributes in self.bot.trans.plugins.reactions.strings.items():
            for trigger in attributes:
                self.commands.append({
                    'command': '(^| )' + trigger + '($| )',
                    'hidden': True
                })
