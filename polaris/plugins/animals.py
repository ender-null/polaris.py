from polaris.utils import send_request, is_command


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.animals.commands
        self.description = self.bot.trans.plugins.animals.description

    # Plugin action #
    def run(self, m):
        if is_command(self, 1, m.content):
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

        elif is_command(self, 2, m.content):
            url = 'https://dog.ceo/api/breeds/image/random'

            data = send_request(url)
            if data:
                self.bot.send_message(m, data.message, 'photo')
            else:
                return self.bot.send_message(m, self.bot.trans.errors.connection_error)