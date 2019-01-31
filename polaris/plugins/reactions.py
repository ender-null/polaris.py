from polaris.utils import get_input, is_command, init_if_empty, wait_until_received, set_data, delete_data, has_tag
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
        if has_tag(self.bot, m.sender.id, 'noreactions') or has_tag(self.bot, m.conversation.id, 'noreactions'):
            return

        for reaction, attributes in self.bot.trans.plugins.reactions.strings.items():
            for trigger in attributes:
                if compile(self.format_text(trigger, m), flags=IGNORECASE).search(m.content):
                    return self.bot.send_message(m, self.format_text(reaction, m), extra={'format': 'markdown'})


    def update_triggers(self):
        self.commands = []

        # Add new triggers #
        for reaction, attributes in self.bot.trans.plugins.reactions.strings.items():
            for trigger in attributes:
                self.commands.append({
                    'command': '(^| )' + self.format_text(trigger) + '\.?($| )',
                    'hidden': True
                })


    def format_text(self, text, message = None):
        text = text.replace('BOT', self.bot.info.username.lower().replace('bot', ''))
        if message:
            text = text.replace('USER', message.sender.first_name)
        return text
