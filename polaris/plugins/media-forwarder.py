from polaris.utils import get_input, has_tag
from copy import deepcopy


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = []
        self.description = None

    # Plugin action #
    def always(self, m):
        id = str(m.conversation.id)
        if has_tag(self.bot, id, 'resend:?') or has_tag(self.bot, id, 'fwd:?'):
            for tag in self.bot.tags[id]:
                if tag.startswith('resend:'):
                    cid = tag.split(':')[1]
                    if m.type == 'photo' or m.type == 'video' or m.type == 'document' or (m.type == 'text' and 'urls' in m.extra):
                        r = deepcopy(m)
                        r.conversation.id = cid
                        
                        if 'urls' in r.extra:
                            for url in r.extra['urls']:
                                self.bot.send_message(r, url, extra={'preview': True})
                        else:
                            self.bot.send_message(r, m.content, m.type, extra={'preview': True})


                elif tag.startswith('fwd:'):
                    cid = tag.split(':')[1]
                    if m.type == 'photo' or m.type == 'document' or m.type == 'url':
                        self.bot.forward_message(cid, m)
