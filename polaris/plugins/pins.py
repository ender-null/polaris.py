from polaris.utils import get_input
from polaris.types import AutosaveDict
from re import findall

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.pins.commands
        self.description = self.bot.trans.plugins.pins.description
        self.pins = AutosaveDict('polaris/data/%s.pins.json' % self.bot.name, defaults={})
        self.update_triggers()

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        # List all pins #
        if self.commands[0]['command'].replace('/', self.bot.config.command_start) in m.content:
            pins = []
            for pin in self.pins:
                if self.pins[pin].creator == m.sender.id:
                    pins.append(pin)

            if len(pins) > 0:
                text = self.bot.trans.plugins.pins.strings.pins % len(pins)
                for pin in pins:
                    text += '\n • #%s' % pin

            else:
                text = self.bot.trans.plugins.pins.strings.no_pins

            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # Add a pin #
        elif self.commands[1]['command'].replace('/', self.bot.config.command_start) in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if input.startswith('#'):
                input = input.lstrip('#')
            input = input.lower()

            if not m.reply:
                return self.bot.send_message(m, self.bot.trans.errors.needs_reply, extra={'format': 'HTML'})

            if input in self.pins:
                return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.already_pinned % input, extra={'format': 'HTML'})

            self.pins[input] = {
                'content': m.reply.content,
                'creator': m.sender.id,
                'type': m.reply.type
            }
            self.pins.store_database()
            self.update_triggers()

            return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.pinned % input, extra={'format': 'HTML'})

        # Remove a pin #
        elif self.commands[2]['command'].replace('/', self.bot.config.command_start) in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if input.startswith('#'):
                input = input.lstrip('#')
            input = input.lower()

            if not input in self.pins:
                return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.not_found % input, extra={'format': 'HTML'})

            if not m.sender.id == self.pins[input]['creator']:
                return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.not_creator % input, extra={'format': 'HTML'})

            del(self.pins[input])
            self.pins.store_database()
            self.update_triggers()

            return self.bot.send_message(m, self.bot.trans.plugins.pins.strings.unpinned % input, extra={'format': 'HTML'})

        # Check what pin was triggered #
        else:
            # Finds the first 3 pins of the message and sends them. #
            pins = findall(r"#(\w+)", m.content.lower())
            count = 3

            for pin in pins:
                if pin in self.pins:
                    # You can reply with a pin and the message will reply too. #
                    if m.reply:
                        reply = m.reply.id
                    else:
                        reply = m.id

                    self.bot.send_message(m, self.pins[pin]['content'], self.pins[pin]['type'], extra={'format': 'HTML'}, reply = reply)
                    count -= 1

                if count == 0:
                    return


    def update_triggers(self):
        # Add new triggers #
        for pin, attributes in self.pins.items():
            if not next((i for i,d in enumerate(self.commands) if 'command' in d and d.command == '#' + pin), None):
                self.commands.append({
                    'command': '#' + pin,
                    'hidden': True
                })

        # Remove unused triggers #
        for command in self.commands:
            if 'hidden' in command and command.hidden and not command.command.lstrip('#') in self.pins:
                self.commands.remove(command)
