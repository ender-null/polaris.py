from polaris.utils import (all_but_first_word, del_tag, first_word,
                           generate_command_help, get_input, has_tag,
                           is_command, is_int, is_owner, is_trusted, set_tag)


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

        if m.reply:
            target = str(m.reply.sender.id)
            name = m.reply.sender.first_name

        elif first_word(input) == '-g':
            target = str(m.conversation.id)
            name = m.conversation.title
            input = all_but_first_word(input)

        elif is_int(first_word(input)):
            target = first_word(input)
            if int(target) > 0 and target in self.bot.users:
                name = self.bot.users[target].first_name
                if '' in self.bot.users[target]:
                    name += ' ' + self.bot.users[target].last_name

            elif int(target) < 0 and target in self.bot.groups:
                name = self.bot.groups[target].title

            else:
                name = target

            input = all_but_first_word(input)

        elif first_word(input).startswith('@'):
            for uid in self.bot.users:
                if 'username' in self.bot.users[uid] and self.bot.users[uid].username and self.bot.users[uid].username.lower() == first_word(input)[1:].lower():
                    target = uid
                    name = self.bot.users[uid].first_name
                    input = all_but_first_word(input)
                    break

        else:
            target = str(m.sender.id)
            name = m.sender.first_name

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
