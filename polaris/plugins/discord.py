from polaris.utils import generate_command_help, get_input


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '/discord',
                'description': 'Discord bot'
            }
        ]

    # Plugin action #
    def run(self, m):
        permissions = 402909206
        url = 'https://discord.com/api/oauth2/authorize?client_id=752912582867812413&permissions={}&scope=bot'.format(
            permissions)
        return self.bot.send_message(m, url, extra={'preview': True})
