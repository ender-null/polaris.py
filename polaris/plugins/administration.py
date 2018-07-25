from polaris.utils import get_input, is_command, first_word, all_but_first_word, is_mod, is_trusted, is_int, set_step, cancel_steps, get_plugin_name, init_if_empty, wait_until_received, set_data, delete_data
from polaris.types import AutosaveDict
from firebase_admin import db
from re import findall


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['administration']['commands']
        self.description = self.bot.trans['plugins']['administration']['description']
        self.administration = wait_until_received('administration/' + self.bot.name)

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        uid = str(m.sender.id)
        gid = str(m.conversation.id)

        # List all administration commands. #
        if is_command(self, 1, m.content):
            text = self.bot.trans['plugins']['administration']['strings']['commands']
            for command in self.commands:
                # Adds the command and parameters#
                if command['command'] == '^new_chat_member$':
                    text += '\n • ' + \
                        self.bot.trans['plugins']['administration']['strings']['new_chat_member']
                else:
                    text += '\n • ' + \
                        command['command'].replace('/', self.bot.config['prefix'])

                if 'parameters' in command:
                    for parameter in command['parameters']:
                        name, required = list(parameter.items())[0]
                        # Bold for required parameters, and italic for optional #
                        if required:
                            text += ' <b>&lt;%s&gt;</b>' % name
                        else:
                            text += ' [%s]' % name

                if 'description' in command:
                    text += '\n   <i>%s</i>' % command['description']
                else:
                    text += '\n   <i>?¿</i>'

            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # List all groups. #
        if is_command(self, 2, m.content):
            text = self.bot.trans['plugins']['administration']['strings']['groups']
            for gid, attr in self.administration.items():
                if self.administration[gid]['public']:
                    if self.administration[gid]['alias']:
                        text += '\n • %s |%s|' % (self.bot.groups[gid]['title'], attr['alias'])
                    else:
                        text += '\n • %s' % (self.bot.groups[gid]['title'])
            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # Join a group. #
        elif is_command(self, 3, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans['errors']['missing_parameter'], extra={'format': 'HTML'})

            for id in self.administration:
                if (input in self.administration or input in self.administration[id]['alias'] or input in self.bot.groups[id]['title']):
                    gid_to_join = id
                    break

            if not gid_to_join in self.administration:
                return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

            text = '<b>%s</b>' % self.bot.groups[gid_to_join]['title']
            if self.administration[gid_to_join]['motd']:
                text += '\n<i>%s</i>' % self.administration[gid_to_join]['motd']

            text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['rules']
            i = 1
            for rule in self.administration[gid_to_join]['rules']:
                text += '\n %s. <i>%s</i>' % (i, rule)
                i += 1
            if not self.administration[gid_to_join]['rules']:
                text += '\n%s' % self.bot.trans['plugins']['administration']['strings']['norules']

            if self.administration[gid_to_join]['public']:
                text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['public_group']
            else:
                text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['private_group']

            if not self.administration[gid_to_join]['link']:
                text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['nolink']
            else:
                text += '\n\n<a href="%s">%s</a>' % (
                    self.administration[gid_to_join]['link'], self.bot.trans['plugins']['administration']['strings']['join'])
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Information about a group. #
        elif is_command(self, 4, m.content) or is_command(self, 9, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})
            if not gid in self.administration:
                if is_command(self, 4, m.content):
                    return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})
                elif is_command(self, 9, m.content):
                    return

            text = '<b>%s</b>' % self.bot.groups[gid]['title']
            if self.administration[gid]['motd']:
                text += '\n<i>%s</i>' % self.administration[gid]['motd']

            text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['rules']
            i = 1
            for rule in self.administration[gid]['rules']:
                text += '\n %s. <i>%s</i>' % (i, rule)
                i += 1

            if not self.administration[gid]['rules']:
                text += '\n%s' % self.bot.trans['plugins']['administration']['strings']['norules']

            if self.administration[gid]['public']:
                text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['public_group']
            else:
                text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['private_group']

            if is_command(self, 4, m.content):
                if not self.administration[gid]['link']:
                    text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['nolink']
                else:
                    text += '\n\n<a href="%s">%s</a>' % (
                        self.bot.trans['plugins']['administration']['strings']['join'], self.administration[gid]['link'])
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Rules of a group. #
        elif is_command(self, 5, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})
            if not gid in self.administration:
                return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

            if input and is_int(input):
                try:
                    i = int(input)
                    text = '%s. <i>%s</i>' % (i,
                                              self.administration[gid]['rules'][i - 1])
                except:
                    text = self.bot.trans['plugins']['administration']['strings']['notfound']

            else:
                text = self.bot.trans['plugins']['administration']['strings']['rules']
                i = 1
                for rule in self.administration[gid]['rules']:
                    text += '\n %s. <i>%s</i>' % (i, rule)
                    i += 1

            if not self.administration[gid]['rules']:
                text += '\n%s' % self.bot.trans['plugins']['administration']['strings']['norules']
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Kicks a user. #
        elif is_command(self, 6, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans['errors']['permission_required'], extra={'format': 'HTML'})

            if not input and not m.reply:
                return self.bot.send_message(m, self.bot.trans['errors']['missing_parameter'], extra={'format': 'HTML'})

            if m.reply:
                target = m.reply.sender.id
            elif input:
                target = input
            else:
                target = m.sender.id

            res = self.bot.kick_user(m, target)
            self.bot.unban_user(m, target)
            if res is None:
                return self.bot.send_message(m, self.bot.trans['errors']['admin_required'], extra={'format': 'HTML'})
            elif not res:
                return self.bot.send_message(m, self.bot.trans['errors']['failed'], extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, '<pre>An enemy has been slain.</pre>', extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans['errors']['unknown'], extra={'format': 'HTML'})

        # Bans a user. #
        elif is_command(self, 7, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans['errors']['permission_required'], extra={'format': 'HTML'})

            if not input:
                return self.bot.send_message(m, self.bot.trans['errors']['missing_parameter'], extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans['errors']['unknown'], extra={'format': 'HTML'})

        # Configures a group. #
        elif is_command(self, 8, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans['errors']['permission_required'], extra={'format': 'HTML'})

            if not input:
                self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['ask_to_add'] % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})
                if not gid in self.administration:
                    self.administration[gid] = {
                        'alias': None,
                        'description': None,
                        'link': None,
                        'rules': [],
                        'public': False
                    }
                    set_data('administration/%s/%s' % (self.bot.name, gid), self.administration[gid])
                set_step(self.bot, m.conversation.id, get_plugin_name(self), 1)
            else:
                if first_word(input) == 'add':
                    if not gid in self.administration:
                        self.administration[gid] = {
                            'alias': None,
                            'description': None,
                            'link': None,
                            'rules': [],
                            'public': False
                        }
                        set_data('administration/%s/%s' % (self.bot.name, gid), self.administration[gid])
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['added'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['already_added'] % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'remove':
                    if gid in self.administration:
                        del self.administration[gid]
                        delete_data('administration/%s/%s' % (self.bot.name, gid))
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['removed'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'alias':
                    if gid in self.administration:
                        self.administration[gid]['alias'] = all_but_first_word(input).lower()
                        set_data('administration/%s/%s/alias' % (self.bot.name, gid), self.administration[gid]['alias'])
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['set'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'motd':
                    if gid in self.administration:
                        self.administration[gid]['motd'] = all_but_first_word(input)
                        set_data('administration/%s/%s/motd' % (self.bot.name, gid), self.administration[gid]['motd'])
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['set'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'link':
                    if gid in self.administration:
                        self.administration[gid]['link'] = all_but_first_word(input)
                        set_data('administration/%s/%s/link' % (self.bot.name, gid), self.administration[gid]['link'])
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['set'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'rules':
                    if gid in self.administration:
                        self.administration[gid]['rules'] = all_but_first_word(all_but_first_word(input).split('\n')[0:])
                        set_data('administration/%s/%s/rules' % (self.bot.name, gid), self.administration[gid]['rules'])
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['set'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'rule':
                    if gid in self.administration:
                        try:
                            i = int(first_word(all_but_first_word(input)))-1
                            if i > len(self.administration[gid]['rules']):
                                i = len(self.administration[gid]['rules'])
                            elif i < 1:
                                i = 0
                        except:
                            return self.bot.send_message(m, self.bot.trans['errors']['unknown'], extra={'format': 'HTML'})
                        self.administration[gid]['rules'].insert(i, all_but_first_word(all_but_first_word(input)))
                        set_data('administration/%s/%s/rules' % (self.bot.name, gid), self.administration[gid]['rules'])
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['set'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'public':
                    if gid in self.administration:
                        if self.bot.trans['plugins']['administration']['strings']['yes'].lower() in all_but_first_word(input).lower():
                            self.administration[gid]['public'] = True
                        else:
                            self.administration[gid]['public'] = False
                        set_data('administration/%s/%s/public' % (self.bot.name, gid), self.administration[gid]['public'])
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['set'] % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

                else:
                    return self.bot.send_message(m, self.bot.trans['errors']['no_results'], extra={'format': 'HTML'})

    def always(self, m):
        if str(m.sender.id).startswith('-100'):
            return

        # Update group data #
        gid = str(m.conversation.id)
        if m.conversation.id < 0:
            if self.bot.groups:
                if gid in self.bot.groups:
                    self.bot.groups[gid]['title'] = m.conversation.title
                    self.bot.groups[gid]['messages'] += 1

                else:
                    self.bot.groups[gid] = {
                        "title": m.conversation.title,
                        "messages": 1
                    }
                set_data('groups/%s/%s' % (self.bot.name, gid), self.bot.groups[gid])

        # Update user data #
        uid = str(m.sender.id)
        if self.bot.users:
            if uid in self.bot.users:
                self.bot.users[uid]['first_name'] = m.sender.first_name
                if hasattr(m.sender, 'last_name'):
                    self.bot.users[uid]['last_name'] = m.sender.last_name
                if hasattr(m.sender, 'username'):
                    self.bot.users[uid]['username'] = m.sender.username
                self.bot.users[uid]['messages'] += 1

            else:
                self.bot.users[uid] = {
                    "first_name": m.sender.first_name,
                    "last_name": m.sender.last_name,
                    "username": m.sender.username,
                    "messages": 1
                }
            set_data('users/%s/%s' % (self.bot.name, uid), self.bot.users[uid])

        # Update group id when upgraded to supergroup #
        if m.type == 'notification' and m.content == 'upgrade_to_supergroup':
            to_id = str(m.extra['chat_id'])
            from_id = str(m.extra['from_chat_id'])
            if from_id in self.administration:
                self.administration[to_id] = self.administration[from_id]
                del self.administration[from_id]
                set_data('administration/%s/%s' % (self.bot.name, to_id), self.administration[to_id])
                delete_data('administration/%s/%s' % (self.bot.name, from_id))

            self.bot.groups[to_id] = self.bot.groups[from_id]
            del self.bot.groups[from_id]
            set_data('groups/%s/%s' % (self.bot.name, to_id), self.bot.groups[to_id])
            delete_data('groups/%s/%s' % (self.bot.name, from_id))


    def steps(self, m, step):
        gid = str(m.conversation.id)

        if step == -1:
            self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['cancel'] % m.conversation.title, extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)

        if step == 0:
            self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['done'] % m.conversation.title, extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)

        elif step == 1:
            if self.bot.trans['plugins']['administration']['strings']['yes'].lower() in m.content.lower():
                set_step(self.bot, m.conversation.id, get_plugin_name(self), 2)
                if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                    self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['ask_link'] % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

            else:
                cancel_steps(self.bot, m.conversation.id)
                self.bot.send_message(m, self.bot.trans['errors']['unknown'], extra={'format': 'HTML'})

        elif step == 2:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 3)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['link'] = m.content
                set_data('administration/%s/%s/link' % (self.bot.name, gid), self.administration[gid]['link'])
                self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['ask_alias'] % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 3:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 4)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['alias'] = m.content.lower()
                set_data('administration/%s/%s/alias' % (self.bot.name, gid), self.administration[gid]['alias'])
                self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['ask_rules'] % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 4:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 5)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['rules'] = m.content.split('\n')
                set_data('administration/%s/%s/rules' % (self.bot.name, gid), self.administration[gid]['rules'])
                self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['ask_motd'] % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 5:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 6)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['motd'] = m.content
                set_data('administration/%s/%s/motd' % (self.bot.name, gid), self.administration[gid]['motd'])
                self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['ask_public'] % m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 6:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), -1)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                if self.bot.trans['plugins']['administration']['strings']['yes'].lower() in m.content.lower():
                    self.administration[gid]['public'] = True
                else:
                    self.administration[gid]['public'] = False
                set_data('administration/%s/%s/public' % (self.bot.name, gid), self.administration[gid]['public'])