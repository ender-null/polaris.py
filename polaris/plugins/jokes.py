import html

from polaris.utils import send_request


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.jokes.commands

    # Plugin action #
    def run(self, m):
        url = 'http://api.icndb.com/jokes/random'
        params = {
            'firstName': self.bot.info.first_name,
            'lastName': self.bot.info.last_name
        }

        data = send_request(url, params, bot=self.bot)

        if not data or data['type'] != 'success':
            return self.bot.send_message(m, self.bot.trans.errors.connection_error)

        self.bot.send_message(m, data.value.joke, extra={'format': 'HTML'})
