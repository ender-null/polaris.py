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

        for pin, attributes in self.pins.items():
            self.commands['#' + pin] = {'hidden': True}

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        # Lists all pins #
        if self.bot.lang.plugins.pins.commands.pins.command.replace('/', self.bot.config.command_start) == m.content:
            text = self.bot.lang.plugins.pins.strings.pins
            for pin in self.pins:
                text += '\n • #%s' % pin
            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # Adds a pin #
        elif self.bot.lang.plugins.pins.commands.pin.command.replace('/', self.bot.config.command_start) in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

            if input.startswith('#'):
                input.lstrip('#')

            if not m.reply:
                return self.bot.send_message(m, self.bot.lang.errors.needs_reply, extra={'format': 'HTML'})

            if input in self.pins:
                return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.already_pinned % input,
                                             extra={'format': 'HTML'})

            self.pins[input] = {
                'content': m.reply.content,
                'creator': m.sender.id,
                'type': m.reply.type
            }
            self.commands['#' + input] = {'hidden': True}
            self.update_triggers()

            return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.pinned % input, extra={'format': 'HTML'})

        # Remove a pin #
        elif self.bot.lang.plugins.pins.commands.unpin.command.replace('/', self.bot.config.command_start) in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

            if input.startswith('#'):
                input.lstrip('#')

            if not input in self.pins:
                return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.not_found % input,
                                             extra={'format': 'HTML'})

            if not m.sender.id == self.pins[input]['creator']:
                return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.not_creator % input,
                                             extra={'format': 'HTML'})

            del(self.pins[input])
            del(self.commands['#' + input])
            self.pins.store_database()
            self.update_triggers()

            return self.bot.send_message(m, self.bot.lang.plugins.pins.strings.unpinned % input,
                                         extra={'format': 'HTML'})

        else:
            for pin, attributes in self.pins.items():
                if pin in m.content:
                    # You can reply with a pin and the message will reply too.
                    if m.reply:
                        reply = m.reply.id
                    else:
                        reply = m.id

                    return self.bot.send_message(m, attributes['content'], attributes['type'], extra={'format': 'HTML'}, reply = reply)

    def update_triggers(self):
        for pin, attributes in self.pins.items():
            self.commands['#' + pin] = {'hidden': True}
                    
