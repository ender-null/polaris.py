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

        if has_tag(self.bot, id, 'resend:?') or has_tag(self.bot, id, 'fwd:?'):
            for tag in self.bot.tags[id]:
                forward = False

                if tag.startswith('resend:') or tag.startswith('fwd:'):
                    cid = tag.split(':')[1]
                    if 'from_chat_id' in m.extra:
                        if str(m.extra['from_chat_id']) == cid:
                            break
                        elif str(m.extra['from_chat_id']) != '0':
                            if has_tag(self.bot, cid, 'resend:?') or has_tag(self.bot, cid, 'fwd:?'):
                                forward = True

                if tag.startswith('resend:') and not forward:
                    cid = tag.split(':')[1]

                    if m.type == 'photo' or m.type == 'video' or m.type == 'animation' or m.type == 'document' or (m.type == 'text' and 'urls' in m.extra):
                        r = deepcopy(m)
                        r.conversation.id = cid
                        r.conversation.title = tag

                        if 'urls' in r.extra:
                            for url in r.extra['urls']:
                                if 'instagram' in url:
                                    url = url.split('?')[0]
                                self.bot.send_message(
                                    r, url, extra={'preview': True})
                        else:
                            self.bot.send_message(
                                r, m.content, m.type, extra={'preview': True})

                    else:
                        logging.info('invalid type: %s' % m.type)

                elif tag.startswith('fwd:') or forward:
                    cid = tag.split(':')[1]
                    if m.type == 'photo' or m.type == 'document' or m.type == 'url':
                        self.bot.forward_message(m, cid)
