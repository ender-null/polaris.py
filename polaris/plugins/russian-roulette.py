from polaris.utils import has_tag, set_tag, del_tag
from random import randint

class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.russian_roulette.commands
        self.description = self.bot.trans.plugins.russian_roulette.description

    # Plugin action #
    def run(self, m):
        uid = m.sender.id
        gid = m.conversation.id

        if gid > 0:
            return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

        bullets = None
        roulette = has_tag(self.bot, gid, 'roulette:?', return_match = True)
        
        if roulette:
            bullets = int(roulette[0].split(':')[1])

        if not bullets:
            set_tag(self.bot, gid, 'roulette:6')
            bullets = 6
        
        if randint(1, bullets) == 1:
            del_tag(self.bot, gid, 'roulette:?')
            set_tag(self.bot, gid, 'roulette:6')

            res = self.bot.kick_user(m, uid)

            if not res:
                self.bot.send_message(m, self.bot.trans.plugins.russian_roulette.strings.cant_bang % m.sender.first_name, extra={'format': 'HTML'})
            else:
                self.bot.send_message(m, self.bot.trans.plugins.russian_roulette.strings.bang % m.sender.first_name, extra={'format': 'HTML'})

        else:
            del_tag(self.bot, gid, 'roulette:%s' % bullets)
            bullets -= 1
            set_tag(self.bot, gid, 'roulette:%s' % bullets)
            text = self.bot.trans.plugins.russian_roulette.strings.empty % (m.sender.first_name, bullets)

            self.bot.send_message(m, text, extra={'format': 'HTML'})
