from polaris.utils import get_input, is_command, is_trusted, has_tag, set_tag, del_tag, first_word, all_but_first_word

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.tags.commands
        self.description = self.bot.trans.plugins.tags.description

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        if not is_trusted(self.bot, m.sender.id):
            return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        if m.reply:
            target = str(m.reply.sender.id)
            name = m.reply.sender.first_name

        elif first_word(input) == '-g':
            target = str(m.conversation.id)
            name = m.conversation.title
            input = all_but_first_word(input)

        elif first_word(input).isdigit():
            target = first_word(input)
            name = target
            input = all_but_first_word(input)

        else:
            target = str(m.sender.id)
            name = m.sender.first_name

        tags = input.split()

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
