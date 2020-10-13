import logging
import re
from re import IGNORECASE, compile

from polaris.utils import (del_tag, fix_telegram_link, get_full_name, has_tag,
                           im_group_admin, is_admin, is_trusted, set_data,
                           set_tag)


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot

    def always(self, m):
        if str(m.conversation.id) == str(self.bot.config.alerts_conversation_id) or str(m.conversation.id) == str(self.bot.config.admin_conversation_id):
            return

        spam_types = ['spam', 'arab', 'russian']

        for spam_type in spam_types:
            if has_tag(self.bot, m.sender.id, spam_type):
                if not is_admin(self.bot, m.sender.id, m):
                    self.kick_spammer(m, spam_type, 'tag')
                elif is_trusted(self.bot, m.sender.id, m):
                    del_tag(self.bot, m.sender.id, spam_type)
                    name = get_full_name(self.bot, m.sender.id)
                    gid = str(m.conversation.id)
                    self.bot.send_admin_alert(
                        'Unmarking %s: %s [%s] from group %s [%s]' % (spam_type, name, m.sender.id, self.bot.groups[gid].title, gid))

            if m.conversation.id < 0 and has_tag(self.bot, m.conversation.id, spam_type) and not has_tag(self.bot, m.conversation.id, 'safe') and not has_tag(self.bot, m.conversation.id, 'resend:?') and not has_tag(self.bot, m.conversation.id, 'fwd:?'):
                self.kick_myself(m)

        if m.extra:
            if 'urls' in m.extra:
                for url in m.extra['urls']:
                    self.check_trusted_telegram_link(
                        m, fix_telegram_link(url))
            if 'caption' in m.extra and m.extra['caption']:
                if self.detect_arab(m.extra['caption']):
                    self.kick_spammer(m, 'arab', 'caption')
                if self.detect_russian(m.extra['caption']):
                    self.kick_spammer(m, 'russian', 'caption')

                try:
                    self.check_trusted_telegram_link(m, m.extra['caption'])
                except:
                    logging.error(m.extra['caption'])

        if not has_tag(self.bot, m.conversation.id, 'safe') and not has_tag(self.bot, m.conversation.id, 'resend:?') and not has_tag(self.bot, m.conversation.id, 'fwd:?'):
            if m.type == 'text':
                if self.detect_arab(m.content):
                    self.kick_spammer(m, 'arab', 'content')

                if self.detect_russian(m.content):
                    self.kick_spammer(m, 'russian', 'content')

            if self.detect_arab(m.sender.first_name):
                self.kick_spammer(m, 'arab', 'name')

            if self.detect_russian(m.sender.first_name):
                self.kick_spammer(m, 'russian', 'name')

    def kick_myself(self, m):
        self.bot.bindings.kick_conversation_member(
            m.conversation.id, self.bot.info.id)
        gid = str(m.conversation.id)
        self.bot.send_admin_alert('Kicked myself from: %s [%s]' % (
            self.bot.groups[gid].title, gid))

    def kick_spammer(self, m, spam_type='spam', content='content'):
        name = get_full_name(self.bot, m.sender.id)
        gid = str(m.conversation.id)
        if content == 'name':
            text = m.sender.first_name
        elif content == 'title':
            text = m.conversation.title
        else:
            text = m.content
        if not has_tag(self.bot, m.sender.id, spam_type):
            self.bot.send_admin_alert(
                'Marked as {}: {} [{}] from group {} [{}] for {}: {}'.format(spam_type, name, m.sender.id, self.bot.groups[gid].title, gid, content, text))
            set_tag(self.bot, m.sender.id, spam_type)
            if spam_type in self.bot.groups[gid]:
                self.bot.groups[gid][spam_type] += 1
            else:
                self.bot.groups[gid][spam_type] = 1
            set_data('groups/%s/%s' %
                     (self.bot.name, gid), self.bot.groups[gid])

            if self.bot.groups[gid][spam_type] >= 10 or str(m.sender.id) == str(m.conversation.id):
                set_tag(self.bot, gid, spam_type)
                self.bot.send_admin_alert(
                    'Marked group as %s: %s [%s]' % (spam_type, self.bot.groups[gid].title, gid))
                if not has_tag(self.bot, m.conversation.id, 'safe') and not has_tag(self.bot, gid, 'resend:?') and not has_tag(self.bot, gid, 'fwd:?'):
                    self.kick_myself(m)

        if im_group_admin(self.bot, m) and has_tag(self.bot, m.conversation.id, 'anti' + spam_type):
            self.bot.bindings.kick_conversation_member(
                m.conversation.id, m.sender.id)
            self.bot.send_admin_alert(
                'Kicked {}: {} [{}] from group {} [{}] for {}: {}'.format(spam_type, name, m.sender.id, self.bot.groups[gid].title, gid, content, text))
            self.bot.send_message(
                m, self.bot.trans.errors.idiot_kicked, extra={'format': 'HTML'})
            self.bot.send_message(m, 'deleteMessage', 'system', extra={
                                  'message_id':  m.id})

    def check_trusted_telegram_link(self, m, text):
        input_match = compile(
            '(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(text)
        if input_match and input_match.group(1):
            trusted_group = False
            if input_match:
                group_hash = input_match.group(1)
                for gid, attr in self.bot.administration.items():
                    group = self.bot.administration[gid]
                    if group and 'link' in group and group_hash in group.link:
                        trusted_group = True
                        break
            if not trusted_group and not is_admin(self.bot, m.sender.id, m):
                name = get_full_name(self.bot, m.sender.id)
                gid = str(m.conversation.id)
                self.bot.send_admin_alert('Sent unsafe telegram link: %s [%s] to group %s [%s] for text: %s' % (
                    name, m.sender.id, self.bot.groups[gid].title, gid, text))
                self.kick_spammer(m, 'spam', 'link')

    def is_trusted_group(self, m):
        for gid in self.bot.administration:
            if str(m.conversation.id) == gid:
                return True

        return False

    def detect_arab(self, text):
        if re.compile(u'[\u0600-\u06FF]').search(str(text)):
            return True

        elif re.compile(u'\u202E').search(str(text)):
            return True

        elif re.compile(u'\u200F').search(str(text)):
            return True

    def detect_russian(self, text):
        if re.compile(u'[А-Яа-яЁё]').search(str(text)):
            return True
