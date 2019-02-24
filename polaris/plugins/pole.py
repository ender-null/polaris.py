from polaris.utils import is_command, wait_until_received, set_data, catch_exception, has_tag, time_in_range
from polaris.types import AutosaveDict
from firebase_admin import db
from firebase_admin.db import ApiCallError
from datetime import datetime, time
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
        now = datetime.now().replace(microsecond=0)
        date = now.isoformat().split('T')[0]
        text = None

        # Pole ranking
        if is_command(self, 1, m.content):
            if time_in_range(time(1, 0, 0), time(2, 0, 0), now.time()):
                type = 1
            elif time_in_range(time(12, 0, 0), time(13, 0, 0), now.time()):
                type = 2
            else:
                type = 0

            if gid in self.bot.poles:
                ranking = DictObject()
                for day in self.bot.poles[gid]:
                    if type == 0:
                        if 'pole' in self.bot.poles[gid][day]:
                            try:
                                ranking[str(self.bot.poles[gid][day].pole)].p += 1
                            except:
                                ranking[str(self.bot.poles[gid][day].pole)] = { 'p': 1, 's': 0, 'f': 0, 'i': 0 }

                        if 'subpole' in self.bot.poles[gid][day]:
                            try:
                                ranking[str(self.bot.poles[gid][day].subpole)].s += 1
                            except:
                                ranking[str(self.bot.poles[gid][day].subpole)] = { 'p': 0, 's': 1, 'f': 0, 'i': 0 }

                        if 'fail' in self.bot.poles[gid][day]:
                            try:
                                ranking[str(self.bot.poles[gid][day].fail)].f += 1
                            except:
                                ranking[str(self.bot.poles[gid][day].fail)] = { 'p': 0, 's': 0, 'f': 1, 'i': 0 }

                        
                        if 'iron' in self.bot.poles[gid][day]:
                            try:
                                ranking[str(self.bot.poles[gid][day].iron)].i += 1
                            except:
                                ranking[str(self.bot.poles[gid][day].iron)] = { 'p': 0, 's': 0, 'f': 0, 'i': 1 }

                    if type == 1:
                        if 'canaria' in self.bot.poles[gid][day]:
                            try:
                                ranking[str(self.bot.poles[gid][day].canaria)].c += 1
                            except:
                                ranking[str(self.bot.poles[gid][day].canaria)] = { 'c': 1 }

                    if type == 2:
                        if 'andaluza' in self.bot.poles[gid][day]:
                            try:
                                ranking[str(self.bot.poles[gid][day].andaluza)].a += 1
                            except:
                                ranking[str(self.bot.poles[gid][day].andaluza)] = { 'a': 1 }

                text = self.bot.trans.plugins.pole.strings.ranking
                for uid, values in self.order_by_points(ranking, type):
                    if type == 0:
                        points = str((values.p * 3) + (values.s * 1) + (values.f * 0.5) + (values.i * 0.1)).rstrip('0').rstrip('.')
                    elif type == 1:
                        points = str(values.c * 1).rstrip('0').rstrip('.')
                    elif type == 2:
                        points = str(values.a * 1).rstrip('0').rstrip('.')
                    text += '\n ' + self.bot.trans.plugins.pole.strings.ranking_points % (self.bot.users[uid].first_name, points)

                if type == 0:
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

                    irons = '\n\n' + self.bot.trans.plugins.pole.strings.irons
                    irons_empty = True
                    for uid, values in self.order_by_irons(ranking):
                        if values.i:
                            irons_empty = False
                            irons += '\n ' + self.bot.trans.plugins.pole.strings.ranking_irons % (self.bot.users[uid].first_name, values.i)
                    if not irons_empty:
                        text += irons

                elif type == 1:
                    poles_canarias = '\n\n' + self.bot.trans.plugins.pole.strings.poles_canarias
                    poles_canarias_empty = True
                    for uid, values in self.order_by_poles_canarias(ranking):
                        if values.c:
                            poles_canarias_empty = False
                            poles_canarias += '\n ' + self.bot.trans.plugins.pole.strings.ranking_poles % (self.bot.users[uid].first_name, values.c)
                    if not poles_canarias_empty:
                        text += poles_canarias

                elif type == 2:
                    poles_andaluzas = '\n\n' + self.bot.trans.plugins.pole.strings.poles_andaluzas
                    poles_andaluzas_empty = True
                    for uid, values in self.order_by_poles_andaluzas(ranking):
                        if values.a:
                            poles_andaluzas_empty = False
                            poles_andaluzas += '\n ' + self.bot.trans.plugins.pole.strings.ranking_poles % (self.bot.users[uid].first_name, values.a)
                    if not poles_andaluzas_empty:
                        text += poles_andaluzas

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


        # Pole canaria
        elif is_command(self, 5, m.content):
            if self.has_pole(gid, uid, date, 1):
                return

            if not time_in_range(time(1, 0, 0), time(2, 0, 0), now.time()):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = DictObject({
                    date: {
                        'canaria': uid
                    }
                })
            else:
                if not date in self.bot.poles[gid]:
                    self.bot.poles[gid][date] = DictObject()

                if not 'canaria' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date].canaria = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            uid = str(uid)
            user = self.bot.users[uid].first_name
            if 'username' in self.bot.users[uid] and self.bot.users[uid].username:
                user = '@' + self.bot.users[uid].username
            text = self.bot.trans.plugins.pole.strings.got_pole_canaria % user


        # Pole andaluza
        elif is_command(self, 6, m.content):
            if self.has_pole(gid, uid, date, 1):
                return

            if not time_in_range(time(12, 0, 0), time(13, 0, 0), now.time()):
                uid = str(uid)
                text = self.bot.trans.plugins.pole.strings.too_soon_for_andaluza % self.bot.users[uid].first_name
                return self.bot.send_message(m, text, extra={'format': 'HTML'})

            if not gid in self.bot.poles:
                self.bot.poles[gid] = DictObject({
                    date: {
                        'andaluza': uid
                    }
                })
            else:
                if not date in self.bot.poles[gid]:
                    self.bot.poles[gid][date] = DictObject()

                if not 'andaluza' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date].andaluza = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            uid = str(uid)
            user = self.bot.users[uid].first_name
            if 'username' in self.bot.users[uid] and self.bot.users[uid].username:
                user = '@' + self.bot.users[uid].username
            text = self.bot.trans.plugins.pole.strings.got_pole_andaluza % user

        # Hierro
        elif is_command(self, 7, m.content):
            if self.has_pole(gid, uid, date):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = DictObject({
                    date: {
                        'iron': uid
                    }
                })
            else:
                if not date in self.bot.poles[gid]:
                    self.bot.poles[gid][date] = DictObject()

                if not 'pole' in self.bot.poles[gid][date] or not 'subpole' in self.bot.poles[gid][date] or not 'fail' in self.bot.poles[gid][date]:
                    uid = str(uid)
                    text = self.bot.trans.plugins.pole.strings.too_soon % self.bot.users[uid].first_name
                    return self.bot.send_message(m, text, extra={'format': 'HTML'})
                elif not 'iron' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date].iron = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            uid = str(uid)
            user = self.bot.users[uid].first_name
            if 'username' in self.bot.users[uid] and self.bot.users[uid].username:
                user = '@' + self.bot.users[uid].username
            text = self.bot.trans.plugins.pole.strings.got_iron % user

        if text:
            self.bot.send_message(m, text, extra={'format': 'HTML'})


    def has_pole(self, gid, uid, date, type = 0):
        # Check if user has pole
        if gid in self.bot.poles and date in self.bot.poles[gid]:
            if type == 0 and (('pole' in self.bot.poles[gid][date] and self.bot.poles[gid][date].pole == uid) or
                ('subpole' in self.bot.poles[gid][date] and self.bot.poles[gid][date].subpole == uid) or
                ('fail' in self.bot.poles[gid][date] and self.bot.poles[gid][date].fail == uid) or
                ('iron' in self.bot.poles[gid][date] and self.bot.poles[gid][date].iron == uid)):
                return True
            elif type == 1 and ('canaria' in self.bot.poles[gid][date] and self.bot.poles[gid][date].canaria == uid):
                return True
            elif type == 2 and ('andaluza' in self.bot.poles[gid][date] and self.bot.poles[gid][date].andaluza == uid):
                return True
        return False


    def order_by_points(self, ranking, type = 0):
        if type == 0:
            return sorted(ranking.items(), key=lambda kv: (kv[1].p * 3) + (kv[1].s * 1) + (kv[1].f * 0.5), reverse=True)
        if type == 1:
            return sorted(ranking.items(), key=lambda kv: (kv[1].c * 1), reverse=True)
        if type == 2:
            return sorted(ranking.items(), key=lambda kv: (kv[1].a * 1), reverse=True)


    def order_by_poles(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].p, reverse=True)


    def order_by_subpoles(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].s, reverse=True)


    def order_by_fails(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].f, reverse=True)


    def order_by_poles_canarias(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].c, reverse=True)


    def order_by_poles_andaluzas(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].a, reverse=True)


    def order_by_iron(self, ranking):
        return sorted(ranking.items(), key=lambda kv: kv[1].i, reverse=True)
