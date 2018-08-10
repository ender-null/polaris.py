from polaris.utils import get_input, is_command, send_request


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.youtube_search.commands
        self.description = self.bot.trans.plugins.youtube_search.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'type': 'video',
            'part': 'snippet',
            'maxResults': '8',
            'q': input,
            'key': self.bot.config.api_keys.google_developer_console
        }

        data = send_request(url, params)

        if 'error' in data or int(data.pageInfo.totalResults) == 0:
            return self.bot.send_message(m, self.bot.trans.errors.no_results)

        if is_command(self, 1, m.content):
            text = 'https://youtu.be/%s' % data['items'][0].id.videoId
        
            self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': True})

        elif is_command(self, 2, m.content):
            text = self.bot.trans.plugins.youtube_search.strings.results % input
            for item in data['items']:
                if len(item.snippet.title) > 26:
                    item.snippet.title = item.snippet.title[:23] + '...'
                text += '\n • <a href="https://youtu.be/%s">%s</a>' % (item.id.videoId, item.snippet.title)

            self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})
