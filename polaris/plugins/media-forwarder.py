import logging
from copy import deepcopy
from re import IGNORECASE, compile

import requests
from polaris.utils import (del_tag, first_word, fix_telegram_link,
                           generate_command_help, get_input, has_tag,
                           is_command, is_int, send_request, set_data, set_tag)


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

        # Remove all resends #
        elif is_command(self, 3, m.content):
            input = get_input(m)
            if not input:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})

            origin = first_word(input)

            if not is_int(origin):
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})

            del_tag(self.bot, origin, 'resend:?')
            del_tag(self.bot, origin, 'fwd:?')
            return self.bot.send_message(m, '✅', extra={'format': 'HTML'})

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

        if m.sender.is_bot:
            logging.info('ignoring bot: {} [{}]'.format(
                m.sender.first_name, m.sender.id))
            return

        if m.sender.id == 777000:
            logging.info('ignoring anonymous message: {} [{}]'.format(
                m.sender.first_name, m.sender.id))
            return

        if has_tag(self.bot, m.sender.id, 'muted'):
            logging.info('ignoring muted user: {} [{}]'.format(
                m.sender.first_name, m.sender.id))
            return

        if 'reply_markup' in m.extra:
            logging.info('ignoring reply markup: {} [{}]'.format(
                m.sender.first_name, m.sender.id))
            return

        if 'via_bot_user_id' in m.extra:
            uid = str(m.extra['via_bot_user_id'])
            name = None

            if uid in self.bot.users:
                name = self.bot.users[uid].first_name

            else:
                info = self.bot.bindings.server_request(
                    'getUser',  {'user_id': int(uid)})
                name = info['first_name']
                self.bot.users[uid] = {
                    'first_name': info['first_name'],
                    'last_name': info['last_name'],
                    'messages': 0
                }
                set_data('users/%s/%s' %
                         (self.bot.name, uid), self.bot.users[uid])

            logging.info('ignoring message via bot: {} [{}]'.format(
                name, m.extra['via_bot_user_id']))
            return

        if has_tag(self.bot, gid, 'resend:?') or has_tag(self.bot, gid, 'fwd:?'):
            for tag in self.bot.tags[gid]:
                forward = False

                if tag.startswith('resend:') or tag.startswith('fwd:'):
                    cid = int(tag.split(':')[1])
                    if 'from_chat_id' in m.extra:
                        if str(m.extra['from_chat_id']) == str(cid):
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

        if has_tag(self.bot, gid, 'discord:?'):
            for tag in self.bot.tags[gid]:
                if tag.startswith('discord:'):
                    token = tag.split(':')[1]
                    webhook_url = 'https://discord.com/api/webhooks/{}'.format(token)

                    if m.type == 'photo' or m.type == 'video' or m.type == 'animation' or m.type == 'document' or (m.type == 'text' and 'urls' in m.extra):
                        if 'urls' in m.extra:
                            for url in m.extra['urls']:
                                input_match = compile(
                                    r'(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(url)

                                if input_match and input_match.group(1) or 'joinchat/' in url:
                                    logging.info(
                                        'ignoring telegram url: {}'.format(fix_telegram_link(url)))
                                else:
                                    if 'instagram' in url:
                                        url = url.split('?')[0]
                                    send_request(webhook_url, {
                                        'content': url
                                    }, post=True)
                        else:
                            if m.content.startswith('http'):
                                send_request(webhook_url, {
                                    'content': m.content
                                }, post=True)
                            else:
                                file = self.bot.get_file(m.content)
                                if file:
                                    send_request(webhook_url, post=True, files={'file': open(file, 'rb')})

                    elif m.type != 'text':
                        logging.info('invalid type: %s' % m.type)
