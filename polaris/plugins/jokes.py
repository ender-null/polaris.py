from polaris.utils import send_request
import html


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.jokes.commands
        self.description = self.bot.trans.plugins.jokes.description

    # Plugin action #
    def run(self, m):
        url = 'http://api.icndb.com/jokes/random'

        data = send_request(url)

        if not data:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error)
            
        text = html.unescape(data.value.joke).replace('Chuck Norris', self.bot.info.first_name)

        self.bot.send_message(m, text)