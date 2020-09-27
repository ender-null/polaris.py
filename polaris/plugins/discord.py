from polaris.utils import generate_command_help, get_input


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.discord.commands

    # Plugin action #
    def run(self, m):
        permissions = 402909206
        url = 'https://discord.com/api/oauth2/authorize?client_id={}&permissions={}&scope=bot'.format(
            self.bot.config.discord_client_id, permissions)
        text = self.bot.trans.plugins.discord.strings.info.format(url)
        return self.bot.send_message(m, text, extra={'format': 'HTML'})
