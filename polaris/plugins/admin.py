import logging
from re import compile, findall

from firebase_admin import db

from polaris.types import AutosaveDict
from polaris.utils import (all_but_first_word, delete_data, get_input,
                           get_target, has_tag, im_group_admin, is_admin,
                           is_command, is_int, is_mod, is_trusted, set_data)


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.admin.commands

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        uid = str(m.sender.id)
        gid = str(m.conversation.id)
        ok = False

        if m.conversation.id > 0:
            return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

        # List all administration commands. #
        if is_command(self, 1, m.content):
            text = self.bot.trans.plugins.admin.strings.commands
            for command in self.commands:
                # Adds the command and parameters#
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

            ok = self.bot.send_message(m, text, extra={'format': 'HTML'})

        # Title #
        if is_command(self, 2, m.content):
            if self.check_permissions(m):
                ok = self.bot.bindings.rename_conversation(
                    m.conversation.id, input)

        # Description #
        elif is_command(self, 3, m.content):
            if self.check_permissions(m):
                ok = self.bot.bindings.change_conversation_description(
                    m.conversation.id, input)

        # Photo #
        elif is_command(self, 4, m.content):
            if self.check_permissions(m):
                if m.reply and m.reply.type == 'photo':
                    photo = self.bot.bindings.get_file(m.reply.content)
                    logging.info(photo)
                    if photo:
                        ok = self.bot.bindings.change_conversation_photo(
                            m.conversation.id, photo)
                    else:
                        ok = self.bot.bindings.change_conversation_photo(
                            m.conversation.id, m.reply.content)

        # Promote #
        elif is_command(self, 5, m.content):
            if self.check_permissions(m):
                target = get_target(self.bot, m, get_input(m))
                ok = self.bot.bindings.promote_conversation_member(
                    m.conversation.id, target)

        # Kick #
        elif is_command(self, 6, m.content):
            if self.check_permissions(m):
                target = get_target(self.bot, m, get_input(m))
                ok = self.bot.bindings.kick_conversation_member(
                    m.conversation.id, target)

        # Unban #
        elif is_command(self, 7, m.content):
            if self.check_permissions(m):
                target = get_target(self.bot, m, get_input(m))
                ok = self.bot.bindings.unban_conversation_member(
                    m.conversation.id, target)

        # Delete message #
        elif is_command(self, 8, m.content):
            if self.check_permissions(m):
                self.bot.bindings.delete_message(m.conversation.id, m.id)
                if m.reply:
                    ok = self.bot.bindings.delete_message(
                        m.conversation.id, m.reply.id)

        # Pin #
        elif is_command(self, 9, m.content):
            if self.check_permissions(m):
                if m.reply:
                    ok = self.bot.send_message(m, 'pinChatMessage', 'system', extra={
                                               'message_id':  m.reply.id})

        # Unpin #
        elif is_command(self, 10, m.content):
            if self.check_permissions(m):
                if m.reply:
                    ok = self.bot.send_message(m, 'unpinChatMessage', 'system')

        # Custom title #
        elif is_command(self, 11, m.content):
            if self.check_permissions(m):
                if m.reply:
                    target = m.reply.sender.id
                else:
                    target = m.sender.id
                ok = self.bot.send_message(m, 'setChatAdministratorCustomTitle', 'api', extra={
                                           'user_id': target, 'custom_title': input})

        # Leave #
        elif is_command(self, 12, m.content):
            if not is_admin(self.bot, m.sender.id) and not is_mod(self.bot, m.sender.id, m.conversation.id):
                self.bot.send_message(
                    m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})
            ok = self.bot.send_message(m, 'leaveChat', 'system')

        if not ok:
            return self.bot.send_message(
                m, self.bot.trans.errors.failed, extra={'format': 'HTML'})

    def check_permissions(self, m):
        if not im_group_admin(self.bot, m):
            self.bot.send_message(
                m, self.bot.trans.errors.admin_required, extra={'format': 'HTML'})
            return False

        if not is_admin(self.bot, m.sender.id) and not is_mod(self.bot, m.sender.id, m.conversation.id):
            self.bot.send_message(
                m, self.bot.trans.errors.permission_required, extra={'format': 'HTML'})
            return False

        return True
