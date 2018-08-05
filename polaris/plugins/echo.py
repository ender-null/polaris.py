from polaris.utils import get_input


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.echo.commands
        self.description = self.bot.trans.plugins.echo.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)

        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        self.bot.send_message(m, input.capitalize(), extra={'format': 'Markdown'})
