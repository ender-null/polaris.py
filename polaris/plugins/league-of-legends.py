import logging
from time import time

from polaris.utils import (all_but_first_word, del_setting, download,
                           first_word, generate_command_help, get_input,
                           get_setting, has_tag, is_command, send_request,
                           set_setting)


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        # self.commands = self.bot.trans.plugins.league_of_legends.commands
        self.commands = [
            {
                'command': '/lol',
                'hidden': True,
                'parameters': [
                    {
                        'summoner name': False
                    }
                ]
            }
        ]

        self.base_url = 'api.riotgames.com'
        self.regions = self.regions_dict()
        self.region = self.regions['euw']
        self.latest_version = self.ddragon_versions()
        self.champions = self.ddragon_champions()
        self.championIds = self.generate_champion_ids()

    # Plugin action #
    def run(self, m):
        input = get_input(m)

        if m.reply:
            uid = str(m.reply.sender.id)
        else:
            uid = str(m.sender.id)

        # Get character data
        if is_command(self, 1, m.content) or is_command(self, 2, m.content) or is_command(self, 3, m.content):
            summoner_name = None

            if not input:
                tags = has_tag(self.bot, m.sender.id,
                               'lol:?', return_match=True)
                if tags and len(tags) > 0:
                    summoner_info = tags[0].split(':')[1]
                    if ('/' in summoner_info):
                        self.region = self.regions[summoner_info.split('/')[0]]
                        summoner_name = summoner_info.split('/')[1]

                if not summoner_name:
                    return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})

            else:
                if first_word(input).lower() in self.regions:
                    self.region = self.regions[first_word(input).lower()]
                    summoner_name = all_but_first_word(input)
                else:
                    self.region = self.regions['euw']
                    summoner_name = input

            summoner = self.summoner_by_name(summoner_name)
            if not summoner or 'status' in summoner and summoner['status']['status_code'] != 200:
                return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

            account = self.account_by_puuid(summoner.puuid)
            masteries = self.champion_masteries(summoner.id)
            ranked = self.league_entries(summoner.id)

            if self.latest_version:
                icon_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(
                    self.latest_version, summoner.profileIconId)

            else:
                icon_url = None

            opgg_region = self.region['platform'] if self.region['platform'] != 'kr' else 'www'
            opgg = 'http://{}.op.gg/summoner/userName={}'.format(
                opgg_region, ''.join(summoner_name.split()))

            text = '%s (Lv: %s)\n%s\n' % (
                summoner.name, summoner.summonerLevel, account.gameName + '#' + account.tagLine)

            if masteries:
                text += '\nMasteries:'
                for mastery in masteries[:3]:
                    text += '\n\t{}: Lv {} ({}k)'.format(
                        self.championIds[str(mastery['championId'])], mastery['championLevel'], int(mastery['championPoints'] / 1000))

            if ranked:
                for queue in ranked:
                    text += '\n\n{}:\n\tLeague: {} {} ({}LP)'.format(
                        self.ranked_queueType(queue['queueType']),
                        self.ranked_tier(queue['tier']),
                        queue['rank'],
                        queue['leaguePoints'])
                    text += '\n\tWins/Losses: {} / {} ({}%)'.format(queue['wins'], queue['losses'],
                                                                    str(int((float(queue['wins']) / (float(queue['wins']) + float(queue['losses']))) * 100)).replace('.', '\''))

            # text += '\n\n<a href="{}">{}</a>'.format(opgg, 'OP.GG')

            if icon_url:
                return self.bot.send_message(m, icon_url, 'photo', extra={
                    'caption': text, 'format': 'HTML', 'preview': True})
            return self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': True})

    def api_request(self, method, params={}, regional=False):
        if regional:
            endpoint = 'https://%s.%s' % (self.region['region'], self.base_url)
        else:
            endpoint = 'https://%s.%s' % (
                self.region['platform'], self.base_url)

        params['api_key'] = self.bot.config.api_keys.riot_api

        return send_request(endpoint + method, params)

    def summoner_by_name(self, summoner_name):
        return self.api_request('/lol/summoner/v4/summoners/by-name/%s' % summoner_name)

    def account_by_puuid(self, puuid):
        return self.api_request('/riot/account/v1/accounts/by-puuid/%s' % puuid, regional=True)

    def champion_masteries(self, encryptedSummonerId):
        return self.api_request('/lol/champion-mastery/v4/champion-masteries/by-summoner/%s' % encryptedSummonerId)

    def league_entries(self, encryptedSummonerId):
        return self.api_request('/lol/league/v4/entries/by-summoner/%s' % encryptedSummonerId)

    def ddragon_versions(self):
        data = send_request(
            'https://ddragon.leagueoflegends.com/api/versions.json')
        if data:
            return data[0]

        return None

    def ddragon_champions(self):
        data = send_request(
            'http://ddragon.leagueoflegends.com/cdn/{}/data/{}/champion.json'.format(self.ddragon_versions(), self.bot.config.locale))
        if data:
            return data.data

        return None

    def ranked_queueType(self, queueType):
        if queueType == 'RANKED_FLEX_SR':
            return 'Ranked Flex'
        elif queueType == 'RANKED_SOLO_5x5':
            return 'Ranked Solo/Duo'
        else:
            return queueType

    def ranked_tier(self, tier):
        return tier.title()

    def generate_champion_ids(self):
        championIds = {}
        for champ in self.champions:
            championIds[self.champions[champ].key] = self.champions[champ].name
        return championIds

    def regions_dict(self):
        return {
            'euw': {
                'platform': 'euw1',
                'region': 'europe'
            },
            'eune': {
                'platform': 'eun1',
                'region': 'europe'
            },
            'tr': {
                'platform': 'tr1',
                'region': 'europe'
            },
            'na': {
                'platform': 'na1',
                'region': 'americas'
            },
            'lan': {
                'platform': 'la1',
                'region': 'americas'
            },
            'las': {
                'platform': 'la2',
                'region': 'americas'
            },
            'lan': {
                'platform': 'la1',
                'region': 'americas'
            },
            'br': {
                'platform': 'br1',
                'region': 'americas'
            },
            'ru': {
                'platform': 'ru',
                'region': 'asia'
            },
            'jp': {
                'platform': 'jp1',
                'region': 'asia'
            },
            'kr': {
                'platform': 'kr',
                'region': 'asia'
            },
            'oce': {
                'platform': 'oc1',
                'region': 'asia'
            }
        }
