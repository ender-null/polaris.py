from polaris.utils import get_input


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            '/help': {
                'hidden': True
            },
            self.bot.lang.plugins.help.commands.help.command: {
                'friendly': self.bot.lang.plugins.help.commands.help.friendly,
                'parameters': self.bot.lang.plugins.help.commands.help.parameters,
            }
        }
        self.description = self.bot.lang.plugins.help.description

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        text = self.bot.lang.plugins.help.strings.commands

        # Iterates the initialized plugins #
        for plugin in self.bot.plugins:
            for command, args in plugin.commands.items():
                # If the command is hidden, ignore it #
                if not 'hidden' in args or not args['hidden']:
                    # Adds the command and parameters#
                    text += '\n • ' + command
                    if 'parameters' in args:
                        for parameter, required in args['parameters'].items():
                            # Bold for required parameters, and italic for optional #
                            if required:
                                text += ' <b>&lt;%s&gt;</b>' % parameter
                            else:
                                text += ' <i>[%s]</i>' % parameter

        self.bot.send_message(m, text, extra={'format': 'HTML'})
