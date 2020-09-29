import json
import logging

from DictObject import DictObject
from polaris.utils import (generate_command_help, get_input, is_command,
                           remove_html)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.help.commands

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        commands = []

        if is_command(self, 2, m.content):
            text = ''
        else:
            text = self.bot.trans.plugins.help.strings.commands

        # Iterates the initialized plugins #
        for plugin in self.bot.plugins:
            if hasattr(plugin, 'commands'):
                for command in plugin.commands:
                    command = DictObject(command)
                    # Adds the command and parameters#
                    if is_command(self, 2, m.content):
                        show = False
                        if 'parameters' in command and command.parameters:
                            allOptional = True
                            for parameter in command.parameters:
                                name, required = list(
                                    parameter.items())[0]
                                if required:
                                    allOptional = False

                            show = allOptional

                        else:
                            show = True

                        if self.bot.config.prefix != '/' and (not 'keep_default' in command or not command.keep_default):
                            show = False

                        if not command.command.startswith('/'):
                            show = False

                        if show:
                            text += '\n' + command.command.lstrip('/')

                            if 'description' in command:
                                text += ' - {}'.format(command.description)
                                commands.append({
                                    'command': command.command.lstrip('/'),
                                    'description': command.description
                                })
                            else:
                                text += ' - No description'
                                commands.append({
                                    'command': command.command.lstrip('/'),
                                    'description': 'No description'
                                })

                    else:
                        # If the command is hidden, ignore it #
                        if not 'hidden' in command or not command.hidden:
                            doc = generate_command_help(
                                plugin, command['command'], False)
                            if doc:
                                lines = doc.splitlines()

                                text += '\n • {}'.format(lines[0])

                                if len(lines) > 1:
                                    text += '\n   {}'.format(lines[1])
                                else:
                                    text += '\n   <i>No description</i>'

        if is_command(self, 2, m.content):
            self.bot.send_message(m, 'setMyCommands', 'api', extra={
                                  'commands': json.dumps(commands)})

        self.bot.send_message(m, text, extra={'format': 'HTML'})

    def inline(self, m):
        input = get_input(m)

        results = []

        for plugin in self.bot.plugins:
            if hasattr(plugin, 'inline') and hasattr(plugin, 'commands'):
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
                                    parameters = ' <b>&lt;{}&gt;</b>'.format(
                                        name)
                                else:
                                    parameters = ' [{}]'.format(name)

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
