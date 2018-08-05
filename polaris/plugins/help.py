from polaris.utils import get_input, is_command, remove_html
from DictObject import DictObject


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.help.commands
        self.commands.append({
            'command': '/help',
            'hidden': True
        })
        self.commands.append({
            'command': '/genhelp',
            'hidden': True
        })
        self.description = self.bot.trans.plugins.help.description

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        if input:
            for plugin in self.bot.plugins:
                text = plugin.description

                for command in plugin.commands:
                    command = DictObject(command)
                    # If the command is hidden, ignore it #
                    if ('hidden' in command and not command.hidden) or not 'hidden' in command:
                        # Adds the command and parameters#
                        if input in command.command.replace('/', '').rstrip('\s'):
                            text += '\n • ' + command.command.replace('/', self.bot.config.prefix)
                            if 'parameters' in command and command.parameters:
                                for parameter in command.parameters:
                                    name, required = list(parameter.items())[0]
                                    # Bold for required parameters, and italic for optional #
                                    if required:
                                        text += ' <b>&lt;%s&gt;</b>' % name
                                    else:
                                        text += ' [%s]' % name

                            if 'description' in command:
                                text += '\n   <i>%s</i>' % command.description
                            else:
                                text += '\n   <i>?¿</i>'

                            return self.bot.send_message(m, text, extra={'format': 'HTML'})
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        if is_command(self, 3, m.content):
            text = ''
        else:
            text = self.bot.trans.plugins.help.strings.commands

        # Iterates the initialized plugins #
        for plugin in self.bot.plugins:
            for command in plugin.commands:
                command = DictObject(command)
                # If the command is hidden, ignore it #
                if not 'hidden' in command or not command.hidden:
                    # Adds the command and parameters#
                    if is_command(self, 3, m.content):
                        show = False
                        if 'parameters' in command and command.parameters:
                            allOptional = True
                            for parameter in command.parameters:
                                name, required = list(parameter.items())[0]
                                if required:
                                    allOptional = False

                            show = allOptional

                        else:
                            show = True

                        if show:
                            text += '\n' + command.command.lstrip('/')

                            if 'description' in command:
                                text += ' - %s' % command.description
                            else:
                                text += ' - ?¿'

                    else:
                        text += '\n • ' + command.command.replace('/', self.bot.config.prefix)
                        if 'parameters' in command and command.parameters:
                            for parameter in command.parameters:
                                name, required = list(parameter.items())[0]
                                # Bold for required parameters, and italic for optional #
                                if required:
                                    text += ' <b>&lt;%s&gt;</b>' % name
                                else:
                                    text += ' [%s]' % name

                        if 'description' in command:
                            text += '\n   <i>%s</i>' % command.description
                        else:
                            text += '\n   <i>?¿</i>'

        self.bot.send_message(m, text, extra={'format': 'HTML'})

    def inline(self, m):
        input = get_input(m)

        results = []

        for plugin in self.bot.plugins:
            if hasattr(plugin, 'inline'):
                for command in plugin.commands:
                    if not 'hidden' in command or not command.hidden:
                        title = command.command.replace('/', '')

                        if 'description' in command:
                            description = command.description
                        else:
                            description = ''

                        parameters = ''
                        if 'parameters' in command and command.parameters:
                            for parameter in command.parameters:
                                name, required = list(parameter.items())[0]
                                # Bold for required parameters, and italic for optional #
                                if required:
                                    parameters = ' <b>&lt;%s&gt;</b>' % name
                                else:
                                    parameters = ' [%s]' % name

                        results.append({
                            'type': 'article',
                            'id': command.command.replace('/', self.bot.config.prefix),
                            'title': title,
                            'input_message_content': {
                                'message_text': command.command.replace('/', self.bot.config.prefix)
                            },
                            'description': description
                        })

        self.bot.answer_inline_query(m, results)
