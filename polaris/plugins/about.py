from polaris.utils import get_input
from firebase_admin import db
import subprocess


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['about']['commands']
        self.commands.append({
            'command': '/start',
            'hidden': True
        })
        self.description = self.bot.trans['plugins']['about']['description']

    # Plugin action #
    def run(self, m):
        tag = subprocess.check_output(['git', 'describe', '--tags']).decode('ascii').rstrip('\n')

        greeting = self.bot.trans['plugins']['about']['strings']['greeting'] % self.bot.info.first_name
        version = self.bot.trans['plugins']['about']['strings']['version'] % tag
        # license = self.bot.trans['plugins']['about']['strings']['license']
        help = self.bot.trans['plugins']['about']['strings']['help'] % self.bot.config['prefix']
        stats = self.bot.trans['plugins']['about']['strings']['stats'] % (len(self.bot.users), len(self.bot.groups))

        text = '%s\n\n%s\n\n%s\n\n%s' % (greeting, help, version, stats)

        self.bot.send_message(m, text, extra={'format': 'HTML'})
