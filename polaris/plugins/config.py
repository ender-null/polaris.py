from polaris.utils import (del_tag, first_word, get_input, has_tag, is_command,
                           is_mod, is_trusted, set_tag)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.config.commands

    # Plugin action #
    def run(self, m):
        if m.conversation.id > 0:
            return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

        input = get_input(m, ignore_reply=False)
        parameter = first_word(input)
        enabled = ['reactions', 'roulette',
                   'replies', 'pole', 'fiesta', 'nsfw']
        disabled = ['antispam', 'antisquig', 'polereset']
        config = {}

        for param in enabled:
            config[param] = not has_tag(
                self.bot, m.conversation.id, 'no' + param)

        for param in disabled:
            config[param] = has_tag(self.bot, m.conversation.id, param)

        text = ''
        if not input:
            text = self.bot.trans.plugins.config.strings.explanation % "', '".join(
                config)
            for param in config:
                text += '\n' + ('✔️' if config[param] else '❌') + \
                    ' ' + self.bot.trans.plugins.config.strings[param]

        elif parameter in enabled or parameter in disabled:
            if not is_trusted(self.bot, m.sender.id, m):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if config[parameter]:
                if parameter in enabled:
                    set_tag(self.bot, m.conversation.id, 'no' + parameter)
                elif parameter in disabled:
                    del_tag(self.bot, m.conversation.id, parameter)
            else:
                if parameter in enabled:
                    del_tag(self.bot, m.conversation.id, 'no' + parameter)
                elif parameter in disabled:
                    set_tag(self.bot, m.conversation.id, parameter)

            text = ('❌' if config[parameter] else '✔️') + \
                ' ' + self.bot.trans.plugins.config.strings[parameter]

        return self.bot.send_message(m, text, extra={'format': 'Markdown'})
