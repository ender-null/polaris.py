import logging
from copy import deepcopy

from polaris.utils import del_tag, get_input, has_tag, set_tag


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = []

    # Plugin action #
    def always(self, m):
        id = str(m.conversation.id)

        if id == '-1001003803132' or id == '-1001339508722':
            logging.info('message from channel: %s' %
                         (m.conversation.title))
            if id in self.bot.tags:
                logging.info('tags S: %s' % self.bot.tags[id])
            elif m.conversation.id in self.bot.tags:
                logging.info('tags I: %s' % self.bot.tags[m.conversation.id])
            else:
                logging.info('no tags for id: %s' % id)

        if has_tag(self.bot, id, 'media:?'):
            del_tag(self.bot, id, 'media:?')
            set_tag(self.bot, id, 'media:%s' % m.id)

        if has_tag(self.bot, id, 'resend:?') or has_tag(self.bot, id, 'fwd:?'):
            logging.info('%s has resend tag: %s' %
                         (m.conversation.id, m.conversation.title))

            if m.conversation.id == m.sender.id:
                self.bot.bindings.delete_message(id, m.id)
                return

            for tag in self.bot.tags[id]:
                if tag.startswith('resend:'):
                    logging.info('found tag: %s' % tag)
                    cid = tag.split(':')[1]
                    if m.type == 'photo' or m.type == 'video' or m.type == 'document' or (m.type == 'text' and 'urls' in m.extra):
                        r = deepcopy(m)
                        r.conversation.id = cid

                        if 'urls' in r.extra:
                            for url in r.extra['urls']:
                                if 'instagram' in url:
                                    url = url.split('?')[0]
                                self.bot.send_message(
                                    r, url, extra={'preview': True})
                        else:
                            self.bot.send_message(
                                r, m.content, m.type, extra={'preview': True})

                elif tag.startswith('fwd:'):
                    logging.info('found tag: %s' % tag)
                    cid = tag.split(':')[1]
                    if m.type == 'photo' or m.type == 'document' or m.type == 'url':
                        self.bot.forward_message(m, cid)

            if not has_tag(self.bot, id, 'media:?'):
                set_tag(self.bot, id, 'media:1')
