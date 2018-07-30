from polaris.utils import get_input


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['info']['commands']
        self.description = self.bot.trans['plugins']['info']['description']

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        gid = str(m.conversation.id)
        if input:
            target = input

        elif m.reply:
            target = str(m.reply.sender.id)

        else:
            target = str(m.sender.id)

        text = ''

        if int(target) > 0:
            if target in self.bot.users:
                if 'first_name' in self.bot.users[target] and self.bot.users[target]['first_name']:
                    user = '\n👤 ' + self.bot.users[target]['first_name']

                if 'last_name' in self.bot.users[target] and self.bot.users[target]['last_name']:
                    user += ' ' + self.bot.users[target]['last_name']

                if 'username' in self.bot.users[target] and self.bot.users[target]['username']:
                    user += '\n@' + self.bot.users[target]['username']
                    
                text = self.bot.trans['plugins']['info']['strings']['user_info'] % (user, target, self.bot.users[target]['messages'])

            if target in self.bot.tags:
                text += '\n🏷 '
                for tag in self.bot.tags[target]:
                    text += tag + ', '
                text = text[:-2]
        else:
            if target in self.bot.groups:
                if 'title' in self.bot.groups[target] and self.bot.groups[target]['title']:
                    group = '\n👥 ' + self.bot.groups[target]['title']

                text = self.bot.trans['plugins']['info']['strings']['group_info'] % (group, target, self.bot.groups[target]['messages'])

            if gid in self.bot.tags:
                text += '\n🏷 '
                for tag in self.bot.tags[gid]:
                    text += tag + ', '
                text = text[:-2]

        if int(gid) < 0 and not input:
            text += '\n\n'
            if gid in self.bot.groups:
                if 'title' in self.bot.groups[gid] and self.bot.groups[gid]['title']:
                    group = '\n👥 ' + self.bot.groups[gid]['title']

                text = self.bot.trans['plugins']['info']['strings']['group_info'] % (group, gid, self.bot.groups[gid]['messages'])

            if gid in self.bot.tags:
                text += '\n🏷 '
                for tag in self.bot.tags[gid]:
                    text += tag + ', '
                text = text[:-2]

        self.bot.send_message(m, text, extra={'format': 'Markdown'})
