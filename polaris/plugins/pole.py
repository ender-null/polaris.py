from polaris.utils import is_command, wait_until_received, set_data, catch_exception
from polaris.types import AutosaveDict
from firebase_admin import db
from firebase_admin.db import ApiCallError
from datetime import datetime
from re import findall
import logging

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['pole']['commands']
        self.description = self.bot.trans['plugins']['pole']['description']

    # Plugin action #
    def run(self, m):
        if m.conversation.id > 0:
            return self.bot.send_message(m, self.bot.trans['errors']['group_only'], extra={'format': 'HTML'})

        gid = str(m.conversation.id)
        uid = m.sender.id
        date = datetime.now().replace(microsecond=0).isoformat().split('T')[0]

        # Pole ranking
        if is_command(self, 1, m.content):
            text = self.bot.trans['errors']['not_implemented']
            if gid in self.bot.poles:
                ranking = {}
                for day in self.bot.poles[gid]:
                    if 'pole' in self.bot.poles[gid][day]:
                        try:
                            ranking[str(self.bot.poles[gid][day]['pole'])]['p'] += 1
                        except:
                            ranking[str(self.bot.poles[gid][day]['pole'])] = { 'p': 1, 's': 0, 'f': 0 }

                    if 'subpole' in self.bot.poles[gid][day]:
                        try:
                            ranking[str(self.bot.poles[gid][day]['subpole'])]['s'] += 1
                        except:
                            ranking[str(self.bot.poles[gid][day]['subpole'])] = { 'p': 0, 's': 1, 'f': 0 }

                    if 'fail' in self.bot.poles[gid][day]:
                        try:
                            ranking[str(self.bot.poles[gid][day]['fail'])]['f'] += 1
                        except:
                            ranking[str(self.bot.poles[gid][day]['fail'])] = { 'p': 0, 's': 0, 'f': 1 }

                text = self.bot.trans['plugins']['pole']['strings']['ranking']
                for uid in self.order_by_points(ranking):
                    points = (ranking[uid]['p'] * 3) + (ranking[uid]['s'] * 1) + (ranking[uid]['f'] * 0.5)
                    text += '\n ' + self.bot.trans['plugins']['pole']['strings']['ranking_points'] % (self.bot.users[uid]['first_name'], points)

        # Pole
        elif is_command(self, 2, m.content):
            if self.has_pole(gid, uid, date):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = {
                    date: {
                        'pole': uid
                    }
                }

            else:
                if not date in self.bot.poles[gid] or not 'pole' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date]['pole'] = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            text = self.bot.trans['plugins']['pole']['strings']['got_pole']

        # Subole
        elif is_command(self, 3, m.content):
            if self.has_pole(gid, uid, date):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = {
                    date: {
                        'subpole': uid
                    }
                }

            else:
                if not date in self.bot.poles[gid] or not 'subpole' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date]['subpole'] = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            text = self.bot.trans['plugins']['pole']['strings']['got_subpole']

        # Fail
        elif is_command(self, 4, m.content):
            if self.has_pole(gid, uid, date):
                return

            if not gid in self.bot.poles:
                self.bot.poles[gid] = {
                    date: {
                        'fail': uid
                    }
                }
            else:
                if not date in self.bot.poles[gid] or not 'fail' in self.bot.poles[gid][date]:
                    self.bot.poles[gid][date]['fail'] = uid
                else:
                    return
            set_data('poles/%s/%s/%s' % (self.bot.name, gid, date), self.bot.poles[gid][date])
            text = self.bot.trans['plugins']['pole']['strings']['got_fail']

        if text:
            self.bot.send_message(m, text, extra={'format': 'HTML'})

    def has_pole(self, gid, uid, date):
        # Check if user has pole
        if (gid in self.bot.poles and date in self.bot.poles[gid] and (
            ('pole' in self.bot.poles[gid][date] and self.bot.poles[gid][date]['pole'] == uid) or
            ('subpole' in self.bot.poles[gid][date] and self.bot.poles[gid][date]['subpole'] == uid) or
            ('fail' in self.bot.poles[gid][date] and self.bot.poles[gid][date]['fail'] == uid))):
            return True
        return False


    def order_by_points(self, ranking):
        return ranking


    def order_by_poles(self, ranking):
        return ranking


    def order_by_subpoles(self, ranking):
        return ranking


    def order_by_fails(self, ranking):
        return ranking
