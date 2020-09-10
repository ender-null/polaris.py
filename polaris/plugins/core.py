import re
import subprocess
import sys
from copy import deepcopy
from io import StringIO
from re import IGNORECASE, compile

from polaris.utils import (all_but_first_word, get_input, get_target, is_admin,
                           is_command, is_owner, is_trusted,
                           wait_until_received)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.core.commands
        self.description = self.bot.trans.plugins.core.description

    # Plugin action #
    def run(self, m):
        if not is_owner(self.bot, m.sender.id) and not is_trusted(self.bot, m.sender.id):
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
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
            target = get_target(self.bot, m, input)
            message = all_but_first_word(input)
            r = deepcopy(m)
            r.conversation.id = target
            self.bot.send_message(r, message)

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

    def always(self, m):
        if m.conversation.id == 777000:
            self.bot.send_admin_alert(m.content)
            self.bot.forward_message(m, self.bot.config.owner)

        if m.extra and 'urls' in m.extra:
            for url in m.extra['urls']:
                input_match = compile(
                    '(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(url)

                if input_match and input_match.group(1):
                    self.bot.join_by_invite_link(url)
