from polaris.utils import get_input, is_admin, is_trusted, is_command, wait_until_received
from io import StringIO
import sys, subprocess


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.core.commands
        self.description = self.bot.trans.plugins.core.description

    # Plugin action #
    def run(self, m):
        if not is_trusted(self.bot, m.sender.id):
            return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

        input = get_input(m)
        text = self.bot.trans.errors.no_results

        # Shutdown
        if is_command(self, 1, m.content):
            self.bot.stop()
            text = self.bot.trans.plugins.core.strings.shutting_down

        # Reload plugins
        elif is_command(self, 2, m.content):
            self.plugins = self.init_plugins()
            text = self.bot.trans.plugins.core.strings.reloading_plugins

        # Reload database
        elif is_command(self, 3, m.content):
            self.bot.get_database()
            text = self.bot.trans.plugins.core.strings.reloading_database

        # Send messages
        elif is_command(self, 4, m.content):
            text = self.bot.trans.errors.not_implemented

        # Run shell commands
        elif is_command(self, 5, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
            return self.bot.send_message(m, '<code>%s</code>' % (subprocess.getoutput(input)), extra={'format': 'HTML'})

        # Run python code
        elif is_command(self, 6, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            cout = StringIO()
            sys.stdout = cout
            cerr = StringIO()
            sys.stderr = cerr

            exec(input)

            if cout.getvalue():
                return self.bot.send_message(m, '<code>%s</code>' % str(cout.getvalue()), extra={'format': 'HTML'})

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        if text:
            self.bot.send_message(m, text, extra={'format': 'HTML'})
