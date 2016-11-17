import requests


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

        res = requests.get(
            url,
            params=params,
        )

        if res.status_code != 200:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error)

        self.bot.send_message(m, res.url, 'photo')
