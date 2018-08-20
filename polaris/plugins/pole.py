from polaris.utils import is_command, wait_until_received, set_data, catch_exception, has_tag
from polaris.types import AutosaveDict
from firebase_admin import db
from firebase_admin.db import ApiCallError
from datetime import datetime
from re import findall
from DictObject import DictObject
import operator

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.pole.commands
        self.description = self.bot.trans.plugins.pole.description

    # Plugin action #
    def run(self, m):
        if m.conversation.id > 0:
            return self.bot.send_message(m, self.bot.trans.errors.group_only, extra={'format': 'HTML'})

        if has_tag(self.bot, m.conversation.id, 'nopole'):
            return

        gid = str(m.conversation.id)
        uid = m.sender.id
        date = datetime.now().replace(microsecond=0).isoformat().split('T')[0]

        # Pole ranking
        if is_command(self, 1, m.content):
            if gid in self.bot.poles:
                ranking = DictObject()
                for day in self.bot.poles[gid]:
                    if 'pole' in self.bot.poles[gid][day]:
                        try:
                            ranking[str(self.bot.poles[gid][day].pole)].p += 1
                        except:
                            ranking[str(self.bot.poles[gid][day].pole)] = { 'p': 1, 's': 0, 'f': 0 }

                    if 'subpole' in self.bot.poles[gid][day]:
                        try:
                            ranking[str(self.bot.poles[gid][day].subpole)].s += 1
                        except:
                            ranking[str(self.bot.poles[gid][day].subpole)] = { 'p': 0, 's': 1, 'f': 0 }

                    if 'fail' in self.bot.poles[gid][day]:
                        try:
                            ranking[str(self.bot.poles[gid][day].fail)].f += 1
                        except:
                            ranking[str(self.bot.poles[gid][day].fail)] = { 'p': 0, 's': 0, 'f': 1 }

                text = self.bot.trans.plugins.pole.strings.ranking
                for uid, values in self.order_by_points(ranking):
                    points = str((values.p * 3) + (values.s * 1) + (values.f * 0.5)).rstrip('0').rstrip('.')
                    text += '\n ' + self.bot.trans.plugins.pole.strings.ranking_points % (self.bot.users[uid].first_name, points)

                poles = '\n\n' + self.bot.trans.plugins.pole.strings.poles
                poles_empty = True
                for uid, values in self.order_by_poles(ranking):
                    if values.p:
                        poles_empty = False
                        poles += '\n ' + self.bot.trans.plugins.pole.strings.ranking_poles % (self.bot.users[uid].first_name, values.p)
                if not poles_empty:
                    text += poles

                subpoles = '\n\n' + self.bot.trans.plugins.pole.strings.subpoles
                subpoles_empty = True
                for uid, values in self.order_by_subpoles(ranking):
                    if values.s:
                        subpoles_empty = False
                        subpoles += '\n ' + self.bot.trans.plugins.pole.strings.ranking_subpoles % (self.bot.users[uid].first_name, values.s)
                if not subpoles_empty:
                    text += subpoles

                fails = '\n\n' + self.bot.trans.plugins.pole.strings.fails
                fails_empty = True
                for uid, values in self.order_by_fails(ranking):
                    if values.f:
                        fails_empty = False
                        fails += '\n ' + self.bot.trans.plugins.pole.strings.ranking_fails % (self.bot.users[uid].first_name, values.f)
                if not fails_empty:
                    text += fails

        # Pole
        elif is_command(self, 2, m.content):
            if self.has_pole(gid, uid, date):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = DictObject({
                    date: {
                        'pole': uid
                    }
                })

            else:
                if not date in self.bot.poles[gid]:
                    self.bot.poles[gid][date] = DictObject()

                if not 'pole' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date].pole = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            uid = str(uid)
            user = self.bot.users[uid].first_name
            if 'username' in self.bot.users[uid] and self.bot.users[uid].username:
                user = '@' + self.bot.users[uid].username
            text = self.bot.trans.plugins.pole.strings.got_pole % user

        # Subole
        elif is_command(self, 3, m.content):
            if self.has_pole(gid, uid, date):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = DictObject({
                    date: {
                        'subpole': uid
                    }
                })

            else:
                if not date in self.bot.poles[gid]:
                    self.bot.poles[gid][date] = DictObject()

                if not 'pole' in self.bot.poles[gid][date]:
                    uid = str(uid)
                    text = self.bot.trans.plugins.pole.strings.too_soon % self.bot.users[uid].first_name
                    return self.bot.send_message(m, text, extra={'format': 'HTML'})
                elif not 'subpole' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date].subpole = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            uid = str(uid)
            user = self.bot.users[uid].first_name
            if 'username' in self.bot.users[uid] and self.bot.users[uid].username:
                user = '@' + self.bot.users[uid].username
            text = self.bot.trans.plugins.pole.strings.got_subpole % user

        # Fail
        elif is_command(self, 4, m.content):
            if self.has_pole(gid, uid, date):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = DictObject({
                    date: {
                        'fail': uid
                    }
                })
            else:
                if not date in self.bot.poles[gid]:
                    self.bot.poles[gid][date] = DictObject()


                if not 'pole' in self.bot.poles[gid][date] or not 'subpole' in self.bot.poles[gid][date]:
                    uid = str(uid)
                    text = self.bot.trans.plugins.pole.strings.too_soon % self.bot.users[uid].first_name
                    return self.bot.send_message(m, text, extra={'format': 'HTML'})
                elif not 'fail' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date].fail = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            uid = str(uid)
            user = self.bot.users[uid].first_name
            if 'username' in self.bot.users[uid] and self.bot.users[uid].username:
                user = '@' + self.bot.users[uid].username
            text = self.bot.trans.plugins.pole.strings.got_fail % user

        if text:
            self.bot.send_message(m, text, extra={'format': 'HTML'})

    def has_pole(self, gid, uid, date):
        # Check if user has pole
        if (gid in self.bot.poles and date in self.bot.poles[gid] and (
            ('pole' in self.bot.poles[gid][date] and self.bot.poles[gid][date].pole == uid) or
            ('subpole' in self.bot.poles[gid][date] and self.bot.poles[gid][date].subpole == uid) or
            ('fail' in self.bot.poles[gid][date] and self.bot.poles[gid][date].fail == uid))):
            return True
        return False


    def order_by_points(self, ranking):
        return sorted(ranking.items(), key=lambda kv: (kv[1].p * 3) + (kv[1].s * 1) + (kv[1].f * 0.5), reverse=True)


    def order_by_poles(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].p, reverse=True)


    def order_by_subpoles(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].s, reverse=True)


    def order_by_fails(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].f, reverse=True)
