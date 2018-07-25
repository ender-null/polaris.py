from polaris.utils import get_input, is_command, remove_html


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['help']['commands']
        self.commands.append({
            'command': '/help',
            'hidden': True
        })
        self.commands.append({
            'command': '/genhelp',
            'hidden': True
        })
        self.description = self.bot.trans['plugins']['help']['description']

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        if input:
            for plugin in self.bot.plugins:
                text = plugin.description

                for command in plugin.commands:

                    # If the command is hidden, ignore it #
                    if 'hidden' in command or not command['hidden']:
                        # Adds the command and parameters#
                        if input in command['command'].replace('/', '').rstrip('\s'):
                            text += '\n • ' + command['command'].replace('/', self.bot.config['prefix'])
                            if 'parameters' in command:
                                for parameter in command['parameters']:
                                    name, required = list(parameter.items())[0]
                                    # Bold for required parameters, and italic for optional #
                                    if required:
                                        text += ' <b>&lt;%s&gt;</b>' % name
                                    else:
                                        text += ' [%s]' % name

                            if 'description' in command:
                                text += '\n   <i>%s</i>' % command['description']
                            else:
                                text += '\n   <i>?¿</i>'

                            return self.bot.send_message(m, text, extra={'format': 'HTML'})
            return self.bot.send_message(m, self.bot.trans['errors']['no_results'], extra={'format': 'HTML'})

        if is_command(self, 3, m.content):
            text = ''
        else:
            text = self.bot.trans['plugins']['help']['strings']['commands']

        # Iterates the initialized plugins #
        for plugin in self.bot.plugins:
            for command in plugin.commands:
                # If the command is hidden, ignore it #
                if not 'hidden' in command or not command['hidden']:
                    # Adds the command and parameters#
                    if self.commands[-1]['command'].replace('/', self.bot.config['prefix']) in m.content:
                        text += '\n' + command['command'].lstrip('/')

                        if 'description' in command:
                            text += ' - %s' % command['description']
                        else:
                            text += ' - ?¿'
                    else:
                        text += '\n • ' + command['command'].replace('/', self.bot.config['prefix'])
                        if 'parameters' in command:
                            for parameter in command['parameters']:
                                name, required = list(parameter.items())[0]
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

    def inline(self, m):
        input = get_input(m)

        results = []
        
        result = {
            'type': 'article',
            'id': '0',
            'title': 'test',
            'input_message_content': {
                'message_text': 'this is a test',
                'parse_mode': 'HTML'
            },
            'description': 'test description'
        }

        results.append(result)

        extra = {
            'switch_pm_text': 'switch to pm',
            'switch_pm_parameter': 'test'
        }

        self.bot.answer_inline_query(m, results, extra)
