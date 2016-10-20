from polaris.utils import get_input


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.lang.plugins.help.commands
        self.commands.append({
            'command': '/help',
            'hidden': True
        })
        self.commands.append({
            'command': '/genhelp',
            'hidden': True
        })
        self.description = self.bot.lang.plugins.help.description

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        
        if self.commands[-1]['command'].replace('/', self.bot.config.command_start) in m.content:
            text = ''
        else:
            text = self.bot.lang.plugins.help.strings.commands

        # Iterates the initialized plugins #
        for plugin in self.bot.plugins:
            for command in plugin.commands:
                # If the command is hidden, ignore it #
                if not 'hidden' in command or not command['hidden']:
                    # Adds the command and parameters#
                    if self.commands[-1]['command'].replace('/', self.bot.config.command_start) in m.content:
                        text += '\n' + command['command'].lstrip('/')

                        if 'description' in command:
                            text += ' - %s' % command['description']
                        else:
                            text += ' - ?¿'
                    else:
                        text += '\n • ' + command['command'].replace('/', self.bot.config.command_start)
                        if 'parameters' in command:
                            for parameter in command['parameters']:
                                name, required = list(parameter.items())[0]
                                print(name)
                                # Bold for required parameters, and italic for optional #
                                if required:
                                    text += ' <b>&lt;%s&gt;</b>' % name
                                else:
                                    text += ' [%s]' % name

                        if 'description' in command:
                            text += '\n   <i>%s</i>' % command['description']
                        else:
                            text += '\n   <i>?¿</i>'

        self.bot.send_message(m, text, extra={'format': 'HTML'})
