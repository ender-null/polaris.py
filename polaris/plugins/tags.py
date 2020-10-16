from polaris.utils import (all_but_first_word, del_tag, first_word,
                           generate_command_help, get_input, get_target,
                           get_username, has_tag, is_command, is_int, is_owner,
                           is_trusted, set_tag)


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.tags.commands
        self.description = self.bot.trans.plugins.tags.description

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        if not is_owner(self.bot, m.sender.id) and not is_trusted(self.bot, m.sender.id):
            return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

        if not input:
            return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
            # return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        if not m.reply:
            input = all_but_first_word(input)

        target = get_target(self.bot, m, get_input(m))
        if target:
            name = get_username(self.bot, target, False)

        elif first_word(input) == '-g':
            target = str(m.conversation.id)
            name = get_username(self.bot, target, False)

        else:
            target = str(m.sender.id)
            name = get_username(self.bot, target, False)

        tags = input.split()

        if not target:
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        # Adds a tag to user or group. #
        if is_command(self, 1, m.content):
            for tag in tags:
                if not has_tag(self.bot, target, tag):
                    set_tag(self.bot, target, tag)
            return self.bot.send_message(m, self.bot.trans.plugins.tags.strings.tagged % (name, tags), extra={'format': 'HTML'})

        # Removes a tag from user or group. #
        elif is_command(self, 2, m.content):
            for tag in tags:
                if has_tag(self.bot, target, tag):
                    del_tag(self.bot, target, tag)
            return self.bot.send_message(m, self.bot.trans.plugins.tags.strings.untagged % (name, tags), extra={'format': 'HTML'})
