import logging

from polaris.utils import has_tag, is_command, send_request


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.animals.commands

    # Plugin action #
    def run(self, m):
        if has_tag(self.bot, m.conversation.id, 'noanimals'):
            return

        if is_command(self, 1, m.content):
            url = 'https://api.thecatapi.com/v1/images/search'
            params = {
                'api_key': self.bot.config.api_keys.cat_api,
                'format': 'src'
            }

            photo = send_request(url, params=params, parse=False, bot=self.bot)

            if photo:
                return self.bot.send_message(m, photo, 'photo')
            else:
                return self.bot.send_message(m, self.bot.trans.errors.connection_error)

        elif is_command(self, 2, m.content):
            url = 'https://dog.ceo/api/breeds/image/random'

            data = send_request(url, bot=self.bot)
            if data:
                return self.bot.send_message(m, data.message, 'photo')
            else:
                return self.bot.send_message(m, self.bot.trans.errors.connection_error)
