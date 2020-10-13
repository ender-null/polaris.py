from re import IGNORECASE, compile, findall

from firebase_admin import db
from polaris.types import AutosaveDict
from polaris.utils import (delete_data, escape_markdown, get_input, has_tag,
                           init_if_empty, is_command, set_data,
                           wait_until_received)


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
                    text = self.format_text(reaction, m)
                    types = ['photo', 'audio', 'document',
                             'voice', 'sticker', 'video']

                    for _type in types:
                        if text.startswith(_type + ':'):
                            content = text.split(':')[1]
                            return self.bot.send_message(m, content, _type)

                    return self.bot.send_message(m, text, extra={'format': 'Markdown'})

    def update_triggers(self):
        self.commands = []

        # Add new triggers #
        for reaction, attributes in self.bot.trans.plugins.reactions.strings.items():
            for trigger in attributes:
                self.commands.append({
                    'command': '(^| )' + self.format_text(trigger) + '\.?($| )',
                    'hidden': True
                })

    def format_text(self, text, message=None):
        text = text.replace(
            'BOT', escape_markdown(self.bot.info.username.lower().replace('bot', '')))
        if message:
            if hasattr(message.sender, 'first_name'):
                text = text.replace('USER', escape_markdown(
                    message.sender.first_name))
            else:
                text = text.replace(
                    'USER', escape_markdown(message.sender.title))
        return text
