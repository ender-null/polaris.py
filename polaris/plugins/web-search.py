import logging

from polaris.utils import get_input, is_command, remove_html, send_request


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.web_search.commands
        self.description = self.bot.trans.plugins.web_search.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        url = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
        params = {
            'q': input,
            'responseFilter': 'Webpages',
            'count': 8,
            'offset': 0,
            'safeSearch': 'Strict',
            'mkt': self.bot.config.locale,
            'setLang': self.bot.config.locale
        }
        headers = {
            'Ocp-Apim-Subscription-Key': self.bot.config.api_keys.microsoft_azure_key
        }
        if is_command(self, 3, m.content):
            params['safeSearch'] = 'Off'

        data = send_request(url, params, headers, bot=self.bot)

        if not data or 'error' in data:
            if 'quota' in data.error.message:
                return self.bot.send_message(m, self.bot.trans.errors.api_limit_exceeded, extra={'format': 'HTML'})
            return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

        if len(data.webPages.value) == 0:
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        if not is_command(self, 2, m.content):
            text = self.bot.trans.plugins.web_search.strings.results % input
            for item in data.webPages.value:
                if len(item.name) > 26:
                    item.name = item.name[:23] + '...'
                text += '\n • <a href="%s">%s</a>' % (item.url, item.name)

            self.bot.send_message(
                m, text, extra={'format': 'HTML', 'preview': False})

        else:
            text = data.webPages.value[0].url

            self.bot.send_message(
                m, text, extra={'format': 'HTML', 'preview': True})
