import logging
from re import IGNORECASE, compile

from polaris.utils import (del_tag, get_full_name, has_tag, im_group_admin,
                           is_admin, is_trusted, set_tag)


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot

    def always(self, m):
        if str(m.sender.id).startswith('-100'):
            return

        if has_tag(self.bot, m.sender.id, 'spam'):
            if not is_admin(self.bot, m.sender.id, m):
                self.kick_spammer(m)
            elif is_trusted(self.bot, m.sender.id, m):
                del_tag(self.bot, m.sender.id, 'spam')
                name = get_full_name(self.bot, m.sender.id)
                gid = str(m.conversation.id)
                self.bot.send_admin_alert(
                    'Unmarking spammer: %s [%s] from group %s [%s]' % (name, m.sender.id, self.bot.groups[gid].title, gid))
        else:
            if m.extra:
                if 'urls' in m.extra:
                    for url in m.extra['urls']:
                        self.check_trusted_telegram_link(m, url)
                if 'caption' in m.extra:
                    self.check_trusted_telegram_link(m, m.extra['caption'])

        if has_tag(self.bot, m.conversation.id, 'spam'):
            self.kick_myself(m)

    def check_trusted_telegram_link(self, m, text):
        input_match = compile(
            '(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(text)
        if input_match and input_match.group(1):
            group_hash = input_match.group(1)
            trusted_group = False
            for gid, attr in self.bot.administration.items():
                group = self.bot.administration[gid]
                if 'link' in group and group_hash in group.link:
                    trusted_group = True
                    break
            if not trusted_group and not is_admin(self.bot, m.sender.id, m):
                name = get_full_name(self.bot, m.sender.id)
                gid = str(m.conversation.id)
                self.bot.send_admin_alert('Sent unsafe telegram link: %s [%s] to group %s [%s]' % (
                    name, m.sender.id, self.bot.groups[gid].title, gid))
                self.kick_spammer(m)

    def is_trusted_group(self, m):
        for gid, attr in self.bot.administration.items():
            if str(m.conversation.id) == gid:
                return True

        return False

    def kick_myself(self, m):
        self.bot.kick_user(m, self.bot.info.id)
        gid = str(m.conversation.id)
        self.bot.send_admin_alert('Kicked myself from: %s [%s]' % (
            self.bot.groups[gid].title, gid))

    def kick_spammer(self, m):
        name = get_full_name(self.bot, m.sender.id)
        gid = str(m.conversation.id)
        if not has_tag(self.bot, m.sender.id, 'spam'):
            self.bot.send_admin_alert(
                'Marked as spammer: %s [%s] from group %s [%s]' % (name, m.sender.id, self.bot.groups[gid].title, gid))
            set_tag(self.bot, m.sender.id, 'spam')

        if im_group_admin(self.bot, m) and has_tag(self.bot, m.conversation.id, 'antispam'):
            self.bot.kick_user(m, m.sender.id)
            self.bot.send_admin_alert(
                'Kicked spammer: %s [%s] from group %s [%s]' % (name, m.sender.id, self.bot.groups[gid].title, gid))
            self.bot.send_message(
                m, self.bot.trans.errors.idiot_kicked, extra={'format': 'HTML'})
