from polaris.utils import get_input
from polaris.types import AutosaveDict


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            self.bot.lang.plugins.pins.commands.pin.command: {
                'friendly': self.bot.lang.plugins.pins.commands.pin.friendly,
                'parameters': self.bot.lang.plugins.pins.commands.pin.parameters
            },
            self.bot.lang.plugins.pins.commands.unpin.command: {
                'friendly': self.bot.lang.plugins.pins.commands.unpin.friendly,
                'parameters': self.bot.lang.plugins.pins.commands.unpin.parameters
            },
            self.bot.lang.plugins.pins.commands.pins.command: {
                'friendly': self.bot.lang.plugins.pins.commands.pins.friendly,
                'parameters': self.bot.lang.plugins.pins.commands.pins.parameters
            }
        }
        self.description = self.bot.lang.plugins.pins.description

        self.pins = AutosaveDict('polaris/data/%s.pins.json' % self.bot.name, defaults={})
        # self.pins.store_database()

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        # Lists all pins #
        if self.bot.lang.plugins.pins.commands.pins.command == m.content:
            text = self.bot.lang.plugins.pins.strings.pins
            for pin in self.pins:
                print(pin)
                text += '\n • %s' % pin
            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # Adds a pin #
        elif self.bot.lang.plugins.pins.commands.pin.command in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

            if not m.reply:
                return self.bot.send_message(m, self.bot.lang.errors.needs_reply, extra={'format': 'HTML'})

            if input in self.pins:
                return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.already_pinned % input,
                                             extra={'format': 'HTML'})

            self.pins[input] = {
                'content': m.reply.content,
                'creator': m.sender.id,
                'type': m.type
            }

            return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.pinned % input, extra={'format': 'HTML'})

        # Remove a pin #
        elif self.bot.lang.plugins.pins.commands.unpin.command in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

            if not input in self.pins:
                return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.not_found % input,
                                             extra={'format': 'HTML'})

            if not m.sender.id == self.pins[input]:
                return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.not_creator % input,
                                             extra={'format': 'HTML'})

            self.pins.remove([input])
            return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.unpinned % input,
                                         extra={'format': 'HTML'})

        else:
            print('kek')
