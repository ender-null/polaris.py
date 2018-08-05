from polaris.utils import download
import requests


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '/belikebill',
                'description': 'Be like %s.' % self.bot.info.first_name
            }
        ]
        self.description = 'Be like %s.' % self.bot.info.first_name

    # Plugin action #
    def run(self, m):
        url = 'http://belikebill.azurewebsites.net/billgen-API.php'
        params = {
            'default': 1,
            'name': self.bot.info.first_name.split()[0],
            'sex': 'f'
        }
        
        photo = download(url, params, extension='.jpg')

        if photo:
            return self.bot.send_message(m, photo, 'photo')
        else:
            return self.bot.send_message(m, self.bot.trans.errors.download_failed)