import logging
import re
import subprocess
import sys
from copy import deepcopy
from io import StringIO
from re import IGNORECASE, compile

from polaris.utils import (all_but_first_word, fix_telegram_link,
                           generate_command_help, get_input, get_target,
                           is_admin, is_command, is_owner, is_trusted,
                           set_data, wait_until_received)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.core.commands
        self.description = self.bot.trans.plugins.core.description
        self.commands.append({
            'command': '/setownname',
            'parameters': [
                {
                    'string': True
                }
            ],
            'hidden': True
        })
        self.commands.append({
            'command': '/setownbio',
            'parameters': [
                {
                    'string': True
                }
            ],
            'hidden': True
        })
        self.commands.append({
            'command': '/setownphoto',
            'hidden': True
        })

    # Plugin action #
    def run(self, m):
        if not is_owner(self.bot, m.sender.id) and not is_trusted(self.bot, m.sender.id):
            return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

        input = get_input(m)
        text = self.bot.trans.errors.no_results

        # Shutdown
        if is_command(self, 1, m.content):
            self.bot.stop()
            text = self.bot.trans.plugins.core.strings.shutting_down

        # Reload plugins
        elif is_command(self, 2, m.content):
            self.bot.plugins = self.bot.init_plugins()
            text = self.bot.trans.plugins.core.strings.reloading_plugins

        # Reload database
        elif is_command(self, 3, m.content):
            self.bot.get_database()
            text = self.bot.trans.plugins.core.strings.reloading_database

        # Send messages
        elif is_command(self, 4, m.content):
            if not input:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
                # return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
            target = get_target(self.bot, m, input)
            message = all_but_first_word(input)
            r = deepcopy(m)
            r.conversation.id = target
            return self.bot.send_message(r, message)

        # Run shell commands
        elif is_command(self, 5, m.content):
            if not input:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
                # return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
            code = '$ %s\n\n%s' % (input, subprocess.getoutput(input))
            return self.bot.send_message(m, '<code class="language-shell">%s</code>' % code, extra={'format': 'HTML'})

        # Run python code
        elif is_command(self, 6, m.content):
            if not input:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
                # return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            cout = StringIO()
            sys.stdout = cout
            cerr = StringIO()
            sys.stderr = cerr

            exec(input)

            code = None
            if cout.getvalue():
                code = '>>>%s\n\n%s' % (input, cout.getvalue())

            if cerr.getvalue():
                code = '>>>%s\n\n%s' % (input, cerr.getvalue())

            if code:
                return self.bot.send_message(m, '<code class="language-python">%s</code>' % code, extra={'format': 'HTML'})

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        # Change name
        elif is_command(self, 7, m.content):
            if not input:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
            ok = self.bot.bindings.server_request(
                'setName',  {'first_name': input, 'last_name': '☆'})

            if not ok:
                text = self.bot.trans.errors.failed

        # Change bio
        elif is_command(self, 8, m.content):
            if not input:
                return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
            ok = self.bot.bindings.server_request(
                'setBio',  {'bio': input})

            if not ok:
                text = self.bot.trans.errors.failed

        # Change photo
        elif is_command(self, 9, m.content):
            ok = False
            if m.reply and m.reply.type == 'photo':
                photo = self.bot.bindings.get_file(m.reply.content)
                if photo:
                    ok = self.bot.bindings.server_request(
                        'setProfilePhoto',  {'photo': self.bot.bindings.get_input_file(photo)})
                else:
                    ok = self.bot.bindings.server_request(
                        'setProfilePhoto',  {'photo': self.bot.bindings.get_input_file(m.reply.content)})

            if not ok:
                text = self.bot.trans.errors.failed

        if text:
            self.bot.send_message(m, text, extra={'format': 'HTML'})

    def always(self, m):
        if m.conversation.id == self.bot.config.alerts_conversation_id or m.conversation.id == self.bot.config.admin_conversation_id:
            return

        if m.sender.id == 777000 and m.conversation.id > 0:
            input_match = compile(r'\d{5}', flags=IGNORECASE).search(m.content)
            if input_match:
                code = u'\u200c'.join([char for char in input_match.group(0)])
                self.bot.send_alert('Login code: {}'.format(code))

        urls = []
        if m.extra and 'urls' in m.extra:
            urls.extend(m.extra['urls'])

        if m.extra and 'reply_markup' in m.extra and m.extra['reply_markup']['@type'] == 'replyMarkupInlineKeyboard':
            for row in m.extra['reply_markup']['rows']:
                for btn in row:
                    if btn['type'] == 'inlineKeyboardButtonTypeUrl':
                        urls.append(btn['url'])

        for url in urls:
            input_match = compile(
                r'(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(url)

            if input_match and input_match.group(1):
                url = fix_telegram_link(url)

                known_link = False
                for gid in self.bot.groups:
                    if 'invite_link' in self.bot.groups[gid] and self.bot.groups[gid]['invite_link'] == url:
                        known_link = True
                        logging.info('known link: {}'.format(url))
                        break

                if not known_link:
                    chat = self.bot.check_invite_link(url)
                    if chat:
                        if chat['chat_id'] == 0:
                            ok = self.bot.join_by_invite_link(url)
                            if ok:
                                cid = str(ok['id'])
                                self.bot.send_admin_alert(
                                    'Joined {} [{}] by invite link: {}'.format(ok['title'], ok['id'], url))
                                if cid in self.bot.groups:
                                    self.bot.groups[cid]['invite_link'] = url
                                    self.bot.groups[cid]['member_count'] = chat['member_count']
                                    self.bot.groups[cid]['title'] = ok['title']

                                else:
                                    self.bot.groups[cid] = {
                                        'invite_link': url,
                                        'member_count': chat['member_count'],
                                        'title': ok['title'],
                                        'messages': 0
                                    }
                                set_data('groups/%s/%s' %
                                         (self.bot.name, cid), self.bot.groups[cid])

                        if gid in self.bot.groups:
                            self.bot.groups[gid]['invite_link'] = url
                            self.bot.groups[gid]['member_count'] = chat['member_count']
                            self.bot.groups[gid]['title'] = chat['title']
                            set_data('groups/%s/%s' %
                                     (self.bot.name, gid), self.bot.groups[gid])

                    else:
                        logging.info(
                            'invalid link: {}'.format(url))
