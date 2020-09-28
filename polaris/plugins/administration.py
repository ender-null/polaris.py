from re import compile, findall

from firebase_admin import db
from polaris.types import AutosaveDict
from polaris.utils import (all_but_first_word, cancel_steps, del_tag,
                           delete_data, first_word, get_input, get_plugin_name,
                           get_target, has_tag, im_group_admin, init_if_empty,
                           is_admin, is_command, is_int, is_mod, is_trusted,
                           set_data, set_step, set_tag, wait_until_received)


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.administration.commands

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        uid = str(m.sender.id)
        gid = str(m.conversation.id)

        # List all administration commands. #
        if is_command(self, 1, m.content):
            text = self.bot.trans.plugins.administration.strings.commands
            for command in self.commands:
                # Adds the command and parameters#
                if command.command == '^new_chat_member$':
                    text += '\n • ' + \
                        self.bot.trans.plugins.administration.strings.new_chat_member
                else:
                    text += '\n • ' + \
                        command.command.replace('/', self.bot.config.prefix)

                if 'parameters' in command and command.parameters:
                    for parameter in command.parameters:
                        name, required = list(parameter.items())[0]
                        # Bold for required parameters, and italic for optional #
                        if required:
                            text += ' <b>&lt;%s&gt;</b>' % name
                        else:
                            text += ' [%s]' % name

                if 'description' in command:
                    text += '\n   <i>%s</i>' % command.description
                else:
                    text += '\n   <i>?¿</i>'

            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        # List all groups. #
        if is_command(self, 2, m.content):
            text = self.bot.trans.plugins.administration.strings.groups
            if len(self.bot.administration) > 0:
                for gid, attr in self.bot.administration.items():
                    if 'public' in self.bot.administration[gid] and self.bot.administration[gid].public:
                        if 'link' in self.bot.administration[gid] and self.bot.config.bindings != 'telegram-cli':
                            text += '\n • <a href="%s">%s</a>' % (
                                self.bot.administration[gid].link, self.bot.groups[gid].title)
                        else:
                            text += '\n • %s' % self.bot.groups[gid].title

                        if self.bot.administration[gid].alias:
                            text += ' /<b>%s</b>/' % attr.alias

            else:
                text = self.bot.trans.plugins.administration.strings.no_groups

            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Join a group. #
        elif is_command(self, 3, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            gid_to_join = None
            for id in self.bot.administration:
                if (input in self.bot.administration
                    or compile('^' + input.lower() + '$').search(self.bot.administration[id].alias.lower())
                        or compile('^' + input.lower() + '$').search(self.bot.groups[id].title.lower())):
                    gid_to_join = id
                    break

            if gid_to_join:
                if not gid_to_join in self.bot.administration:
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

                added = self.bot.bindings.invite_conversation_member(
                    gid_to_join, uid)

                if not added:
                    text = '<b>%s</b>' % self.bot.groups[gid_to_join].title
                    if self.bot.administration[gid_to_join].motd:
                        text += '\n<i>%s</i>' % self.bot.administration[gid_to_join].motd

                    text += '\n\n%s' % self.bot.trans.plugins.administration.strings.rules
                    i = 1
                    if 'rules' in self.bot.administration[gid_to_join]:
                        for rule in self.bot.administration[gid_to_join].rules:
                            text += '\n %s. <i>%s</i>' % (i, rule)
                            i += 1
                    else:
                        text += '\n%s' % self.bot.trans.plugins.administration.strings.norules

                    if not self.bot.administration[gid_to_join].link:
                        text += '\n\n%s' % self.bot.trans.plugins.administration.strings.nolink
                    else:
                        text += '\n\n<a href="%s">%s</a>' % (
                            self.bot.administration[gid_to_join].link, self.bot.trans.plugins.administration.strings.join)
                    return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Information about a group. #
        elif is_command(self, 4, m.content) or is_command(self, 16, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})
            if not gid in self.bot.administration:
                if is_command(self, 4, m.content):
                    return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})
                elif is_command(self, 16, m.content):
                    return

            text = '<b>%s</b>' % self.bot.groups[gid].title
            if 'motd' in self.bot.administration[gid]:
                text += '\n<i>%s</i>' % self.bot.administration[gid].motd

            text += '\n\n%s' % self.bot.trans.plugins.administration.strings.rules
            i = 1

            if not 'rules' in self.bot.administration[gid]:
                text += '\n%s' % self.bot.trans.plugins.administration.strings.norules
            else:
                for rule in self.bot.administration[gid].rules:
                    text += '\n %s. <i>%s</i>' % (i, rule)
                    i += 1

            if is_command(self, 4, m.content):
                if not self.bot.administration[gid].link:
                    text += '\n\n%s' % self.bot.trans.plugins.administration.strings.nolink
                else:
                    text += '\n\n<a href="%s">%s</a>' % (
                        self.bot.trans.plugins.administration.strings.join, self.bot.administration[gid].link)
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Rules of a group. #
        elif is_command(self, 5, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})
            if not gid in self.bot.administration:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

            if input and is_int(input):
                try:
                    i = int(input)
                    text = '%s. <i>%s</i>' % (i,
                                              self.bot.administration[gid].rules[i - 1])
                except:
                    text = self.bot.trans.plugins.administration.strings.notfound

            else:
                text = self.bot.trans.plugins.administration.strings.rules
                i = 1
                for rule in self.bot.administration[gid].rules:
                    text += '\n %s. <i>%s</i>' % (i, rule)
                    i += 1

            if not self.bot.administration[gid].rules:
                text += '\n%s' % self.bot.trans.plugins.administration.strings.norules
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})

        # Set rules #
        elif is_command(self, 6, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m) and not is_mod(self.bot, uid, gid):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if gid in self.bot.administration:
                self.bot.administration[gid].rules = input.split('\n')
                set_data('administration/%s/%s/rules' %
                         (self.bot.name, gid), self.bot.administration[gid].rules)
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

        # Set rule #
        elif is_command(self, 7, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m) and not is_mod(self.bot, uid, gid):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if gid in self.bot.administration:
                try:
                    i = int(first_word(input))-1
                    if i > len(self.bot.administration[gid].rules):
                        i = len(self.bot.administration[gid].rules)
                    elif i < 1:
                        i = 0
                except:
                    return self.bot.send_message(m, self.bot.trans.errors.invalid_syntax, extra={'format': 'HTML'})

                self.bot.administration[gid].rules.insert(
                    i, all_but_first_word(input))
                set_data('administration/%s/%s/rules' %
                         (self.bot.name, gid), self.bot.administration[gid].rules)
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})

        # Remove rule #
        elif is_command(self, 8, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m) and not is_mod(self.bot, uid, gid):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if gid in self.bot.administration:
                try:
                    i = int(first_word(input))-1
                    if i > len(self.bot.administration[gid].rules):
                        i = len(self.bot.administration[gid].rules)
                    elif i < 1:
                        i = 0
                except:
                    return self.bot.send_message(m, self.bot.trans.errors.invalid_syntax, extra={'format': 'HTML'})

                del self.bot.administration[gid].rules[i]
                set_data('administration/%s/%s/rules' %
                         (self.bot.name, gid), self.bot.administration[gid].rules)
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})

        # Add mod #
        elif is_command(self, 9, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            set_tag(self.bot, m.sender.id, 'mod:%s' % gid)

        # Remove mod #
        elif is_command(self, 10, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, gid):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            del_tag(self.bot, m.sender.id, 'mod:%s' % gid)

        # Add group #
        elif is_command(self, 11, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if not gid in self.bot.administration:
                self.bot.administration[gid] = {
                    'alias': None,
                    'description': None,
                    'link': None,
                    'rules': [],
                    'public': False
                }
                set_data('administration/%s/%s' %
                         (self.bot.name, gid), self.bot.administration[gid])
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.added % m.conversation.title, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.already_added % m.conversation.title, extra={'format': 'HTML'})

        # Remove group #
        elif is_command(self, 12, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if gid in self.bot.administration:
                del self.bot.administration[gid]
                delete_data('administration/%s/%s' % (self.bot.name, gid))
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.removed % m.conversation.title, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

        # Set alias #
        elif is_command(self, 13, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if gid in self.bot.administration:
                self.bot.administration[gid].alias = input.lower()
                set_data('administration/%s/%s/alias' %
                         (self.bot.name, gid), self.bot.administration[gid].alias)
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

        # Set link #
        elif is_command(self, 14, m.content):
            if m.conversation.id > 0:
                return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

            if not is_admin(self.bot, uid, m):
                return self.bot.send_message(m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})

            if gid in self.bot.administration:
                self.bot.administration[gid].link = input.lower()
                set_data('administration/%s/%s/link' %
                         (self.bot.name, gid), self.bot.administration[gid].link)
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

        # Make public #
        elif is_command(self, 15, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            if gid in self.bot.administration:
                if input and 'true' in input.lower():
                    self.bot.administration[gid].public = True
                else:
                    self.bot.administration[gid].public = False
                set_data('administration/%s/%s/public' %
                         (self.bot.name, gid), self.bot.administration[gid].public)
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.set % m.conversation.title, extra={'format': 'HTML'})
            else:
                return self.bot.send_message(m, self.bot.trans.plugins.administration.strings.not_added % m.conversation.title, extra={'format': 'HTML'})

    def always(self, m):
        # Update group id when upgraded to supergroup #
        if m.type == 'notification' and m.content == 'upgrade_to_supergroup':
            to_id = str(m.extra['chat_id'])
            from_id = str(m.extra['from_chat_id'])
            if from_id in self.bot.administration:
                self.bot.administration[to_id] = self.bot.administration[from_id]
                del self.bot.administration[from_id]
                set_data('administration/%s/%s' %
                         (self.bot.name, to_id), self.bot.administration[to_id])
                delete_data('administration/%s/%s' % (self.bot.name, from_id))

            self.bot.groups[to_id] = self.bot.groups[from_id]
            del self.bot.groups[from_id]
            set_data('groups/%s/%s' %
                     (self.bot.name, to_id), self.bot.groups[to_id])
            delete_data('groups/%s/%s' % (self.bot.name, from_id))
