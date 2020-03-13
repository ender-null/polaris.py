from polaris.utils import set_tag, has_tag, del_tag, is_admin, is_trusted, im_group_admin
from re import compile, IGNORECASE
import logging


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot

    def always(self, m):
        if str(m.sender.id).startswith('-100'):
            return

        if has_tag(self.bot, m.sender.id, 'spam') and self.is_trusted_group(m):
            if not is_admin(self.bot, m.sender.id, m):
                self.kick_spammer(m)
            elif is_trusted(self.bot, m.sender.id, m):
                del_tag(self.bot, m.sender.id, 'spam')
        else:
            if m.extra and 'urls' in m.extra:
                for url in m.extra['urls']:
                    self.check_trusted_telegram_link(m, url)

        if has_tag(self.bot, m.conversation.id, 'spam'):
            self.kick_myself(m)

    def check_trusted_telegram_link(self, m, text):
        input_match = compile('(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(text)
        if input_match and input_match.group(1):
            group_hash = input_match.group(1)
            trusted_group = False;
            for gid, attr in self.bot.administration.items():
                group = self.bot.administration[gid]
                if 'link' in group and group_hash in group.link:
                    trusted_group = True
                    break
            if not trusted_group and not is_admin(self.bot, m.sender.id, m):
                self.kick_spammer(m)

    def is_trusted_group(self, m):
        for gid, attr in self.bot.administration.items():
            if str(m.conversation.id) == gid:
                return True

        return False

    def kick_myself(self, m):
        self.bot.kick_user(m, self.bot.info.id)

    def kick_spammer(self, m):
        set_tag(self.bot, m.sender.id, 'spam')
        if im_group_admin(self.bot, m):
            self.bot.kick_user(m, m.sender.id)
            self.bot.send_message(m, self.bot.trans.errors.idiot_kicked, extra={'format': 'HTML'})
