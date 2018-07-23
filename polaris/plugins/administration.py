from polaris.utils import get_input, is_command, first_word, all_but_first_word, is_mod, is_trusted, is_int, set_step, cancel_steps, get_plugin_name
from polaris.types import AutosaveDict
from firebase_admin import db
from re import findall


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['administration']['commands']
        self.description = self.bot.trans['plugins']['administration']['description']
        self.administration = db.reference('administration').child(self.bot.name)
        self.cached_administration = self.administration.get()
        self.groups = db.reference('groups').child(self.bot.name)
        self.cached_groups = self.groups.get()
        self.users = db.reference('users').child(self.bot.name)
        self.cached_users = self.users.get()

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
            for gid, attr in self.cached_administration.items():
                text += '\n • %s |%s|' % (self.cached_groups[gid]['title'], attr['alias'])
            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # Join a group. #
        elif is_command(self, 3, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans['errors']['missing_parameter'], extra={'format': 'HTML'})

            for id in self.cached_administration:
                if (input in self.cached_administration or
                    input in self.cached_administration[id]['alias'] or
                        input in self.cached_groups[id]['title']):
                    gid_to_join = id
                    break

            if not gid_to_join in self.cached_administration:
                return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

            text = '<b>%s</b>\n<i>%s</i>\n\n%s' % (self.cached_groups[gid_to_join]['title'], self.cached_administration[gid_to_join]
                                                   ['description'], self.bot.trans['plugins']['administration']['strings']['rules'])
            i = 1
            for rule in self.cached_administration[gid_to_join]['rules']:
                text += '\n %s. <i>%s</i>' % (i, rule)
                i += 1
            if not self.cached_administration[gid_to_join]['rules']:
                text += '\n%s' % self.bot.trans['plugins']['administration']['strings']['norules']
            if not self.cached_administration[gid_to_join]['link']:
                text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['nolink']
            else:
                text += '\n\n<a href="%s">%s</a>' % (
                    self.cached_administration[gid_to_join]['link'], self.bot.trans['plugins']['administration']['strings']['join'])
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Information about a group. #
        elif is_command(self, 4, m.content) or is_command(self, 9, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})
            if not gid in self.cached_administration:
                if is_command(self, 4, m.content):
                    return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})
                elif is_command(self, 9, m.content):
                    return

            text = '<b>%s</b>\n<i>%s</i>\n\n%s' % (self.cached_groups[gid]['title'], self.cached_administration[gid]
                                                   ['description'], self.bot.trans['plugins']['administration']['strings']['rules'])
            i = 1
            for rule in self.cached_administration[gid]['rules']:
                text += '\n %s. <i>%s</i>' % (i, rule)
                i += 1

            if not self.administration[gid]['rules']:
                text += '\n%s' % self.bot.trans['plugins']['administration']['strings']['norules']
            if is_command(self, 4, m.content):
                if not self.cached_administration[gid]['link']:
                    text += '\n\n%s' % self.bot.trans['plugins']['administration']['strings']['nolink']
                else:
                    text += '\n\n<a href="%s">%s</a>' % (
                        self.bot.trans['plugins']['administration']['strings']['join'], self.administration[gid]['link'])
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Rules of a group. #
        elif is_command(self, 5, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})
            if not gid in self.cached_administration:
                return self.bot.send_message(m, self.bot.trans['plugins']['administration']['strings']['not_added'] % m.conversation.title, extra={'format': 'HTML'})

            if input and is_int(input):
                try:
                    i = int(input)
                    text = '%s. <i>%s</i>' % (i,
                                              self.cached_administration[gid]['rules'][i - 1])
                except:
                    text = self.bot.trans['plugins']['administration']['strings']['notfound']

            else:
                text = self.bot.trans['plugins']['administration']['strings']['rules']
                i = 1
                for rule in self.cached_administration[gid]['rules']:
                    text += '\n %s. <i>%s</i>' % (i, rule)
                    i += 1

            if not self.cached_administration[gid]['rules']:
                text += '\n%s' % self.bot.trans['plugins']['administration']['strings']['norules']
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Kicks a user. #
        elif is_command(self, 6, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input and not m.reply:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if m.reply:
                target = m.reply.sender.id
            elif input:
                target = input
            else:
                target = m.sender.id

            res = self.bot.kick_user(m, target)
            self.bot.unban_user(m, target)
            if res is None:
                return self.bot.send_message(m, self.bot.trans.errors.admin_required, extra={'format': 'HTML'})
            elif not res:
                return self.bot.send_message(m, self.bot.trans.errors.failed, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, '<pre>An enemy has been slain.</pre>', extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Bans a user. #
        elif is_command(self, 7, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id, m.conversation.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        # Configures a group. #
        elif is_command(self, 8, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_mod(self.bot, m.sender.id):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not input:
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_to_add %
                                      m.conversation.title, extra={'format': 'HTML', 'force_reply': True})
                if not gid in self.administration:
                    self.administration[gid] = {
                        'alias': None,
                        'description': None,
                        'link': None,
                        'rules': []
                    }
                    self.administration.store_database()
                set_step(self.bot, m.conversation.id, get_plugin_name(self), 1)
            else:
                if first_word(input) == 'add':
                    if not gid in self.administration:
                        self.administration[gid] = {
                            'alias': None,
                            'description': None,
                            'link': None,
                            'rules': []
                        }
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.added % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.already_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'remove':
                    if gid in self.administration:
                        del(self.administration[gid])
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.removed % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'alias':
                    if gid in self.administration:
                        self.administration[gid]['alias'] = all_but_first_word(
                            input)
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'motd':
                    if gid in self.administration:
                        self.administration[gid]['description'] = all_but_first_word(
                            input)
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'link':
                    if gid in self.administration:
                        self.administration[gid]['link'] = all_but_first_word(
                            input)
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'rules':
                    if self.administration and gid in self.administration:
                        self.administration[gid]['rules'] = all_but_first_word(input).split('\n')[
                            0:]
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                elif first_word(input) == 'rule':
                    if self.administration and gid in self.administration:
                        try:
                            i = int(first_word(all_but_first_word(input)))-1
                            if i > len(self.administration[gid]['rules']):
                                i = len(self.administration[gid]['rules'])
                            elif i < 1:
                                i = 0
                        except:
                            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})
                        self.administration[gid]['rules'].insert(
                            i, all_but_first_word(all_but_first_word(input)))
                        self.administration.store_database()
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
                    else:
                        return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                else:
                    return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

    def always(self, m):
        if str(m.sender.id).startswith('-100'):
            return

        # Update group data #
        gid = str(m.conversation.id)
        if m.conversation.id < 0:
            groups = self.groups.get()
            if groups:
                if gid in groups:
                    grp = groups[gid]
                    grp['title'] = m.conversation.title
                    grp['messages'] += 1
                    self.groups.child(gid).update(grp)

                else:
                    grp = {
                        "title": m.conversation.title,
                        "messages": 1
                    }
                    self.groups.child(gid).set(grp)

        # Update user data #
        uid = str(m.sender.id)
        users = self.users.get()
        if users:
            if uid in users:
                usr = users[uid]
                usr['first_name'] = m.sender.first_name
                if hasattr(m.sender, 'last_name'):
                    usr['last_name'] = m.sender.last_name
                if hasattr(m.sender, 'username'):
                    usr['username'] = m.sender.username
                usr['messages'] += 1
                self.users.child(uid).update(usr)

            else:
                usr = {
                    "first_name": m.sender.first_name,
                    "last_name": m.sender.last_name,
                    "username": m.sender.username,
                    "messages": 1
                }
                self.users.child(uid).set(usr)

        # Update group id when upgraded to supergroup #
        if m.type == 'notification' and m.content == 'upgrade_to_supergroup':
            to_id = str(m.extra['chat_id'])
            from_id = str(m.extra['from_chat_id'])
            if from_id in self.administration:
                self.administration[to_id] = self.administration.pop(from_id)
            self.groups[to_id] = self.groups.pop(from_id)

        # self.administration.store_database()
        # self.groups.store_database()
        # self.users.store_database()

    def steps(self, m, step):
        gid = str(m.conversation.id)

        if step == -1:
            self.bot.send_message(m, self.bot.trans.plugins.administration.strings.cancel %
                                  m.conversation.title, extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)

        if step == 0:
            self.bot.send_message(m, self.bot.trans.plugins.administration.strings.done %
                                  m.conversation.title, extra={'format': 'HTML'})
            cancel_steps(self.bot, m.conversation.id)

        elif step == 1:
            if self.bot.trans.plugins.administration.strings.yes.lower() in m.content.lower():
                set_step(self.bot, m.conversation.id, get_plugin_name(self), 2)
                if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                    self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_link %
                                          m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

            else:
                cancel_steps(self.bot, m.conversation.id)
                self.bot.send_message(
                    m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        elif step == 2:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 3)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['link'] = m.content
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_alias %
                                      m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 3:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 4)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['alias'] = m.content.lower()
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_rules %
                                      m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 4:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), 5)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['rules'] = m.content.split('\n')
                self.bot.send_message(m, self.bot.trans.plugins.administration.strings.ask_motd %
                                      m.conversation.title, extra={'format': 'HTML', 'force_reply': True})

        elif step == 5:
            set_step(self.bot, m.conversation.id, get_plugin_name(self), -1)
            if not m.content.startswith('/cancel') and not m.content.startswith('/done'):
                self.administration[gid]['motd'] = m.content
