import logging
from copy import deepcopy
from re import IGNORECASE, compile

from polaris.utils import (del_tag, first_word, fix_telegram_link,
                           generate_command_help, get_input, has_tag,
                           is_command, set_tag)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '/resends',
                'hidden': True
            },
            {
                'command': '/addresend',
                'hidden': True
            },
            {
                'command': '/rmresend',
                'hidden': True
            }
        ]

    # Plugin action #
    def run(self, m):
        # List #
        if is_command(self, 1, m.content):
            resends = []
            forwards = []
            text = ''
            for gid in self.bot.tags:
                for tag in self.bot.tags[gid]:
                    if 'resend:' in tag:
                        resends.append('{}:{}'.format(gid, tag.split(':')[1]))

                    if 'fwd:' in tag:
                        resends.append('{}:{}'.format(gid, tag.split(':')[1]))

            if len(resends) > 0:
                text += '<b>Resends:</b>'
                text += self.generate_text(resends)

            if len(forwards) > 0:
                text += '\n<b>Forwards:</b>'
                text += self.generate_text(forwards)

            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # Add resend #
        elif is_command(self, 2, m.content):
            input = get_input(m)
            if not input:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})

            origin = first_word(input)
            destination = first_word(input, 2)

            if not origin or not destination:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})

    def generate_text(self, items):
        text = ''
        for item in items:
            orig = item.split(':')[0]
            dest = item.split(':')[1]

            text += '\n'

            if orig in self.bot.groups:
                text += '\t{} [{}]'.format(self.bot.groups[orig].title, orig)
            else:
                text += '\t{}'.format(orig)

            if dest in self.bot.groups:
                text += ' ➡️ {} [{}]'.format(self.bot.groups[dest].title, dest)
            else:
                text += ' ➡️ {}'.format(dest)

            text += '\n'

        return text

    # Plugin action #
    def always(self, m):
        gid = str(m.conversation.id)

        if 'via_bot_user_id' in m.extra:
            logging.info('ignoring message via bot: {}'.format(
                m.extra['via_bot_user_id']))
            return

        if has_tag(self.bot, gid, 'resend:?') or has_tag(self.bot, gid, 'fwd:?'):
            for tag in self.bot.tags[gid]:
                forward = False

                if tag.startswith('resend:') or tag.startswith('fwd:'):
                    cid = int(tag.split(':')[1])
                    if 'from_chat_id' in m.extra:
                        if str(m.extra['from_chat_id']) == cid:
                            break
                        elif str(m.extra['from_chat_id']) != '0':
                            if has_tag(self.bot, cid, 'resend:?') or has_tag(self.bot, cid, 'fwd:?'):
                                logging.info('forward')
                                forward = True

                    logging.info('tag: {}, forward: {}'.format(tag, forward))

                if tag.startswith('resend:') and not forward:
                    cid = int(tag.split(':')[1])

                    if m.type == 'photo' or m.type == 'video' or m.type == 'animation' or m.type == 'document' or (m.type == 'text' and 'urls' in m.extra):
                        r = deepcopy(m)
                        r.conversation.id = cid
                        r.conversation.title = tag

                        if 'urls' in r.extra:
                            for url in r.extra['urls']:
                                input_match = compile(
                                    r'(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(url)

                                if input_match and input_match.group(1) or 'joinchat/' in url:
                                    logging.info(
                                        'ignoring telegram url: {}'.format(fix_telegram_link(url)))
                                else:
                                    if 'instagram' in url:
                                        url = url.split('?')[0]
                                    self.bot.send_message(
                                        r, url, extra={'preview': True})
                        else:
                            self.bot.send_message(
                                r, m.content, m.type, extra={'preview': True})

                    elif m.type != 'text':
                        logging.info('invalid type: %s' % m.type)

                elif tag.startswith('fwd:') or forward:
                    cid = int(tag.split(':')[1])
                    if m.type == 'photo' or m.type == 'document' or m.type == 'url':
                        self.bot.forward_message(m, cid)
