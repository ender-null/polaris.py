from polaris.utils import get_input
import subprocess


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.lang.plugins.about.commands
        self.commands.append({
            'command': '/start',
            'hidden': True
        })
        self.description = self.bot.lang.plugins.about.description

    # Plugin action #
    def run(self, m):
        tag = subprocess.check_output(['git', 'describe', '--tags']).decode('ascii').rstrip('\n')
        # commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').rstrip('\n')
        # branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('ascii').rstrip('\n')

        greeting = self.bot.lang.plugins.about.strings.greeting % self.bot.info.first_name
        version = self.bot.lang.plugins.about.strings.version % (tag)
        # license = self.bot.lang.plugins.about.strings.license
        help = self.bot.lang.plugins.about.strings.help % self.bot.config.command_start

        text = '%s\n\n%s\n\n%s' % (greeting, help, version)

        self.bot.send_message(m, text, extra={'format': 'HTML'})
