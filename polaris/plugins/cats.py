from polaris.utils import send_request


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.cats.commands
        self.description = self.bot.trans.plugins.help.description

    # Plugin action #
    def run(self, m):
        url = 'http://thecatapi.com/api/images/get'
        params = {
            'format': 'src',
            'api_key': self.bot.config.api_keys.cat_api
        }

        photo = send_request(url, params=params, parse=False)

        if photo:
            self.bot.send_message(m, photo, 'photo')
        else:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error)