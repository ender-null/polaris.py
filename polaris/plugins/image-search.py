from random import randint

from polaris.utils import download, get_input, is_command, send_request


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.image_search.commands
        self.description = self.bot.trans.plugins.image_search.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        url = 'https://api.cognitive.microsoft.com/bing/v7.0/images/search'
        params = {
            'q': input,
            'count': 8,
            'offset': 0,
            'safeSearch': 'Strict',
            'mkt': self.bot.config.locale,
            'setLang': self.bot.config.locale
        }
        if is_command(self, 1, m.content):
            params['safeSearch'] = 'Off'

        headers = {
            'Ocp-Apim-Subscription-Key': self.bot.config.api_keys.microsoft_azure_key
        }

        data = send_request(url, params, headers, bot=self.bot)

        if not data or data['_type'] == 'ErrorResponse':
            return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

        if len(data.value) == 0:
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        try:
            i = randint(0, len(data.value) - 1)
            photo = data.value[i].contentUrl
            caption = None  # data.value[i].name

        except Exception as e:
            self.bot.send_alert(e)
            photo = None

        if photo:
            return self.bot.send_message(m, photo, 'photo', extra={'caption': caption})
        else:
            return self.bot.send_message(m, self.bot.trans.errors.download_failed)
