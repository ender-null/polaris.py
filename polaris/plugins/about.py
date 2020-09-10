import subprocess

from firebase_admin import db

from polaris.utils import get_input, has_tag, is_command, set_data


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.about.commands
        self.commands.append({
            'command': '/start',
            'hidden': True,
            'keep_default': True
        })

    # Plugin action #
    def run(self, m):
        text = None
        if is_command(self, 1, m.content) or is_command(self, 3, m.content):
            tag = subprocess.check_output(
                ['git', 'describe', '--tags']).decode('ascii').rstrip('\n')

            greeting = self.bot.trans.plugins.about.strings.greeting % self.bot.info.first_name
            version = self.bot.trans.plugins.about.strings.version % tag
            license = self.bot.trans.plugins.about.strings.license
            help = self.bot.trans.plugins.about.strings.help % self.bot.config.prefix
            donations = self.bot.trans.plugins.about.strings.donations % self.bot.config.prefix
            stats = self.bot.trans.plugins.about.strings.stats % (
                len(self.bot.users), len(self.bot.groups))

            if is_command(self, 1, m.content):
                text = '%s\n\n%s\n\n%s\n%s\n\n%s\n\n%s' % (
                    greeting, help, version, donations, license, stats)

            else:
                text = '%s\n\n%s\n\n%s' % (greeting, help, donations)

        elif is_command(self, 2, m.content):
            donations_explanation = self.bot.trans.plugins.about.strings.donations_explanation
            supporters_title = self.bot.trans.plugins.about.strings.supporters
            supporters = ''
            for uid in self.bot.users:
                if has_tag(self.bot, uid, 'supporter') or has_tag(self.bot, uid, 'supporter:?'):
                    supporters += '\n • %s' % self.bot.users[uid].first_name
                    if 'last_name' in self.bot.users[uid] and self.bot.users[uid].last_name:
                        supporters += ' %s' % self.bot.users[uid].last_name
                    if 'username' in self.bot.users[uid] and self.bot.users[uid].username:
                        supporters += ' @%s' % self.bot.users[uid].username

                    for tag in has_tag(self.bot, uid, 'supporter:?', True):
                        if ':' in tag:
                            supporters += ' | %s' % tag.split(':')[1]

            if len(supporters) > 0:
                text = '%s\n\n%s%s' % (
                    donations_explanation, supporters_title, supporters)
            else:
                text = donations_explanation

        self.bot.send_message(
            m, text, extra={'format': 'HTML', 'preview': False})

    def always(self, m):
        # Update group data #
        gid = str(m.conversation.id)
        if m.conversation.id < 0:
            if self.bot.groups:
                if gid in self.bot.groups:
                    self.bot.groups[gid].title = m.conversation.title
                    self.bot.groups[gid].messages += 1

                else:
                    self.bot.groups[gid] = {
                        "title": m.conversation.title,
                        "messages": 1
                    }
                set_data('groups/%s/%s' %
                         (self.bot.name, gid), self.bot.groups[gid])

        # Update user data #
        if str(m.sender.id).startswith('-100'):
            return

        uid = str(m.sender.id)
        if self.bot.users:
            if uid in self.bot.users:
                self.bot.users[uid].first_name = m.sender.first_name
                if hasattr(m.sender, 'last_name'):
                    self.bot.users[uid].last_name = m.sender.last_name
                if hasattr(m.sender, 'username'):
                    self.bot.users[uid].username = m.sender.username
                if hasattr(m.sender, 'is_bot'):
                    self.bot.users[uid].is_bot = m.sender.is_bot
                self.bot.users[uid].messages += 1

            else:
                self.bot.users[uid] = {
                    "first_name": m.sender.first_name,
                    "last_name": m.sender.last_name,
                    "username": m.sender.username,
                    "messages": 1
                }
            set_data('users/%s/%s' % (self.bot.name, uid), self.bot.users[uid])
