from polaris.utils import get_input, is_command, send_request, download, set_setting, get_setting, del_setting
from time import time


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.world_of_warcraft.commands
        self.description = self.bot.trans.plugins.world_of_warcraft.description

    # Plugin action #
    def run(self, m):

        input = get_input(m)
        if m.reply:
            uid = str(m.reply.sender.id)
        else:
            uid = str(m.sender.id)

        # Get character data
        if is_command(self, 1, m.content) or is_command(self, 2, m.content) or is_command(self, 3, m.content):
            if not input:
                wow = get_setting(self.bot, uid, 'wow')
                if wow:
                    realm = ' '.join(wow.split('/')[:-1])
                    character = wow.split('/')[-1]
                else:
                    return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
            else:
                realm = ' '.join(input.split()[:-1])
                character = input.split()[-1]
                
            if is_command(self, 1, m.content):
                region = 'eu'
                locale = 'en_GB'
                if self.bot.config.translation != 'default':
                    locale = 'es_ES'

            elif is_command(self, 2, m.content):
                region = 'us'
                locale = 'en_US'
                if self.bot.config.translation != 'default':
                    locale = 'es_MX'

            elif is_command(self, 3, m.content):
                set_setting(self.bot, uid, 'wow', '%s/%s' % (realm, character))
                text = self.bot.trans.plugins.world_of_warcraft.strings.character_set % (character.title(), realm.title())
                return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': True})

            url = 'https://%s.api.battle.net/wow/character/%s/%s' % (region, realm, character)
            params = {
                'fields': 'guild,progression,items',
                'locale': locale,
                'apikey': self.bot.config.api_keys.battle_net
            }

            data = send_request(url, params)

            if not data or 'status' in data:
                return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

            render_url = 'https://render-%s.worldofwarcraft.com/character/' % region
            photo = render_url + data.thumbnail.replace('avatar', 'main') + '?update=%s' % int(time() / 3600)
            name = self.bot.trans.plugins.world_of_warcraft.strings.name % (data.name, data.realm, data.level)
            race = self.bot.trans.plugins.world_of_warcraft.strings.race % (self.get_race(data.race, region), self.get_class(data['class'], region), self.get_gender(data.gender))
            stats = self.bot.trans.plugins.world_of_warcraft.strings.stats % (data['items'].averageItemLevelEquipped, data.achievementPoints, data.totalHonorableKills)
            progression = self.get_raids(data.progression.raids)

            if 'guild' in data:
                guild = '\n&lt;%s-%s&gt;' % (data.guild.name, data.guild.realm)
            else:
                guild = None

            text = '<a href="%s">⁣</a>' % photo

            if guild:
                text += name + guild + race + stats + progression
            else:
                text += name + race + stats + progression

            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': True})

        # Reset character
        elif is_command(self, 4, m.content):
            del_setting(self.bot, uid, 'wow')
            text = self.bot.trans.plugins.world_of_warcraft.strings.character_reset
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': True})

        # Token price
        elif is_command(self, 5, m.content):
            url = 'https://wowtokenprices.com/current_prices.json'
            data = send_request(url)

            if data:
                text = self.bot.trans.plugins.world_of_warcraft.strings.token_title
                for region in data:
                    text += self.bot.trans.plugins.world_of_warcraft.strings.token_price % (
                        region.upper(), int(data[region].current_price / 1000),
                        int(data[region]['1_day_low'] / 1000), int(data[region]['1_day_high'] / 1000))

                return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': True})

            else:
                return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML', 'preview': True})


    def get_class(self, class_id, region):
        locale = 'en_GB'
        if self.bot.config.translation != 'default':
            locale = 'es_ES'

        url = 'https://%s.api.battle.net/wow/data/character/classes' % region
        params = {
            'locale': locale,
            'apikey': self.bot.config.api_keys.battle_net
        }

        data = send_request(url, params)
        for class_ in data.classes:
            if class_.id == class_id:
                return class_.name


    def get_race(self, race_id, region):
        locale = 'en_GB'
        if self.bot.config.translation != 'default':
            locale = 'es_ES'

        url = 'https://%s.api.battle.net/wow/data/character/races' % region
        params = {
            'locale': locale,
            'apikey': self.bot.config.api_keys.battle_net
        }

        data = send_request(url, params)
        for race in data.races:
            if race.id == race_id:
                return race.name


    def get_gender(self, gender_id):
        if gender_id == 1:
            return self.bot.trans.plugins.world_of_warcraft.strings.female
        else:
            return self.bot.trans.plugins.world_of_warcraft.strings.male


    def get_raids(self, raids):
        progression = '\n'
        progression += '\n' + raids[-1].name
        progression += self.bot.trans.plugins.world_of_warcraft.strings.lfr_raid + self.get_raid_kills(raids[-1].bosses, 0)
        progression += self.bot.trans.plugins.world_of_warcraft.strings.normal_raid + self.get_raid_kills(raids[-1].bosses, 1)
        progression += self.bot.trans.plugins.world_of_warcraft.strings.heroic_raid + self.get_raid_kills(raids[-1].bosses, 2)
        progression += self.bot.trans.plugins.world_of_warcraft.strings.mythic_raid + self.get_raid_kills(raids[-1].bosses, 3)

        return progression

    def get_raid_kills(self, bosses, tier):
        total = 0
        kills = 0
        for boss in bosses:
            total += 1
            if tier == 0 and boss.lfrKills > 0:
                kills += 1
            elif tier == 1 and boss.normalKills > 0:
                kills += 1
            elif tier == 2 and boss.heroicKills > 0:
                kills += 1
            elif tier == 3 and boss.mythicKills > 0:
                kills += 1

        return '%s/%s' % (kills, total)