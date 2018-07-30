from polaris.utils import get_input, is_admin, is_trusted, is_command, wait_until_received
from io import StringIO
import sys, subprocess


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['core']['commands']
        self.description = self.bot.trans['plugins']['core']['description']

    # Plugin action #
    def run(self, m):
        if not is_trusted(self.bot, m.sender.id):
            return self.bot.send_message(m, self.bot.trans['errors']['permission_required'], extra={'format': 'HTML'})

        input = get_input(m)
        text = self.bot.trans['errors']['no_results']

        # Shutdown
        if is_command(self, 1, m.content):
            self.bot.started = False
            text = self.bot.trans['plugins']['core']['strings']['shutting_down']

        # Restart
        elif is_command(self, 2, m.content):
            self.bot.start()
            text = self.bot.trans['plugins']['core']['strings']['restarting']

        # Reload
        elif is_command(self, 3, m.content):
            self.bot.config = wait_until_received('bots/' + self.bot.name)
            self.bot.trans = wait_until_received('translations/' + self.bot.config['translation'])
            self.bot.users = wait_until_received('users/' + self.bot.name)
            self.bot.groups = wait_until_received('groups/' + self.bot.name)
            self.bot.steps = wait_until_received('steps/' + self.bot.name)
            self.bot.tags = wait_until_received('tags/' + self.bot.name)
            self.bot.settings = wait_until_received('settings/' + self.bot.name)
            text = self.bot.trans['plugins']['core']['strings']['reloading']

        # Send messages
        elif is_command(self, 4, m.content):
            text = self.bot.trans['errors']['not_implemented']

        # Run shell commands
        elif is_command(self, 5, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans['errors']['missing_parameter'], extra={'format': 'HTML'})
            text = '<code>%s</code>' % (subprocess.getoutput(input))

        # Run python code
        elif is_command(self, 6, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans['errors']['missing_parameter'], extra={'format': 'HTML'})

            cout = StringIO()
            sys.stdout = cout
            cerr = StringIO()
            sys.stderr = cerr

            exec(input)

            if cout.getvalue():
                text = '<code>%s</code>' % str(cout.getvalue())

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        if text:
            self.bot.send_message(m, text, extra={'format': 'HTML'})
