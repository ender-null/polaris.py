from polaris.utils import get_input, get_coords, send_request, download, remove_html
import requests, json, logging


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            self.bot.lang.plugins.cats.commands.cat.command: {
                'friendly': self.bot.lang.plugins.cats.commands.cat.friendly,
            },
        }
        self.description = self.bot.lang.plugins.help.description

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
            return self.bot.send_message(m, self.bot.lang.errors.connection_error)

        photo = download(url, params)

        if photo:
            self.bot.send_message(m, photo, 'photo')
        else:
            self.bot.send_message(m, self.bot.lang.errors.missing_parameter, 'text')
