from polaris.utils import get_input, send_request, remove_html


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

        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': input,
            'alt': 'json',
            'num': 8,
            'start': 1,
            'key': self.bot.config.api_keys.google_developer_console,
            'cx': self.bot.config.api_keys.google_custom_search_engine
        }

        data = send_request(url, params)

        if not data:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error)

        if data.searchInformation.totalResults == 0:
            return self.bot.send_message(m, self.bot.trans.errors.no_results)

        message = self.bot.trans.plugins.web_search.strings.results % input
        for item in data['items']:
            if len(item['title']) > 26:
                item['title'] = item['title'][:23] + '...'
            message += '\n • <a href="%s">%s</a>' % (item['link'], item['title'])

        return self.bot.send_message(m, message, extra={'format': 'HTML', 'preview': False})
