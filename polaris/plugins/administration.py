from polaris.utils import get_input, is_command, first_word, is_mod
from polaris.types import AutosaveDict
from re import findall

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.administration.commands
        self.description = self.bot.trans.plugins.administration.description
        self.administration = AutosaveDict('polaris/data/%s.administration.json' % self.bot.name)
        self.groups = AutosaveDict('polaris/data/%s.groups.json' % self.bot.name)
        self.users = AutosaveDict('polaris/data/%s.users.json' % self.bot.name)

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        uid = str(m.sender.id)
        gid = str(m.conversation.id)

        # List all administration commands. #
        if is_command(self, 1, m.content):
            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # List all groups. #
        if is_command(self, 2, m.content):
            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Join a group. #
        elif is_command(self, 3, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Information about a group. #
        elif is_command(self, 4, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Rules of a group. #
        elif is_command(self, 5, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Kicks a user. #
        elif is_command(self, 6, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input and not m.reply:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if m.reply:
                target = m.reply.sender.id
            elif input:
                target = input
            else:
                target = m.sender.id
                
            res = self.bot.kick_user(m, target)
            self.bot.unban_user(m, target)
            if res is None:
                return self.bot.send_message(m, self.bot.trans.errors.admin_required, extra={'format': 'HTML'})
            elif not res:
                return self.bot.send_message(m, self.bot.trans.errors.failed, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, '<pre>An enemy has been slain.</pre>', extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Bans a user. #
        elif is_command(self, 7, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Configures a group. #
        elif is_command(self, 8, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_trusted(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if first_word(input) == 'add':
                if not gid in self.administration:
                    self.administration[gid]
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.added % m.conversation.title, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.already_added % m.conversation.title, extra={'format': 'HTML'})

            elif first_word(input) == 'remove':
                if gid in self.administration:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.removed % m.conversation.title, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            elif first_word(input) == 'alias':
                if gid in self.administration:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            elif first_word(input) == 'description':
                if gid in self.administration:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            elif first_word(input) == 'rules':
                if gid in self.administration:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            elif first_word(input) == 'rule':
                if str(m.conversation.id) in self.administration:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            else:
                return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})


    def always(self, m):
        if str(m.sender.id).startswith('-100'):
            return

        # Update group data #
        gid = str(m.conversation.id)
        if m.conversation.id < 0:
            if gid in self.groups:
                self.groups[gid].title = m.conversation.title
                self.groups[gid].messages += 1

            else:
                self.groups[gid] = {
                    "title": m.conversation.title,
                    "messages": 1
                }
        self.groups.store_database()

        # Update user data #
        uid = str(m.sender.id)
        if uid in self.users:
            self.users[uid].first_name = m.sender.first_name
            if hasattr(m.sender, 'last_name'):
                self.users[uid].last_name = m.sender.last_name
            if hasattr(m.sender, 'username'):
                self.users[uid].username = m.sender.username
            self.users[uid].messages += 1

        else:
            self.users[uid] = {
                "first_name": m.sender.first_name,
                "last_name": m.sender.last_name,
                "username": m.sender.username,
                "messages": 1
            }

        # Update group id when upgraded to supergroup #
        if m.type == 'notification' and m.content == 'upgrade_to_supergroup':
            to_id = str(m.extra['chat_id'])
            from_id = str(m.extra['from_chat_id'])
            self.groups[to_id] = self.groups.pop(from_id)
            print('upgraded')

        self.users.store_database()
