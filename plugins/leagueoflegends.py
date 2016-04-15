from core.utils import *
from bs4 import BeautifulSoup

commands = [
    ('/lol', ['summoner']),
    ('/br ', ['summoner']),
    ('/eune ', ['summoner']),
    ('/euw ', ['summoner']),
    ('/kr ', ['summoner']),
    ('/lan ', ['summoner']),
    ('/las ', ['summoner']),
    ('/na ', ['summoner']),
    ('/oce ', ['summoner']),
    ('/ru ', ['summoner']),
    ('/tr ', ['summoner'])
]
description = 'Gets stats from League of Legends summoner.'
hidden = True


def get_server(m):
    if not server:
        if get_command(m) == 'br':
            return 'br'
        elif get_command(m) == 'eune':
            return 'eune'
        elif get_command(m) == 'kr':
            return 'kr'
        elif get_command(m) == 'lan':
            return 'lan'
        elif get_command(m) == 'las':
            return 'las'
        elif get_command(m) == 'na':
            return 'na'
        elif get_command(m) == 'oce':
            return 'oce'
        elif get_command(m) == 'ru':
            return 'ru'
        elif get_command(m) == 'tr':
            return 'tr'
        else:
            return 'euw'
    else:
        return server


def get_summoner(server, name):
    url = 'https://' + server + '.api.pvp.net/api/lol/' + server + '/v1.4/summoner/by-name/' + name
    params = {
        'api_key': config.keys.league_of_legends
    }
    return send_request(url, params)


def get_summoner_icon(server, summoner, summoner_name):
    versions_url = 'https://global.api.pvp.net/api/lol/static-data/euw/v1.2/versions'
    params = {
        'api_key': config.keys.league_of_legends
    }
    url = 'http://ddragon.leagueoflegends.com/cdn/%s/img/profileicon/' % (send_request(versions_url, params)[0])
    return url + str(summoner[summoner_name]['profileIconId']) + '.png'


def get_stats(server, summoner_id):
    url = 'https://%s.api.pvp.net//api/lol/%s/v1.3/stats/by-summoner/%s/summary' % (server, server, summoner_id)
    params = {
        'api_key': config.keys.league_of_legends
    }

    return send_request(url, params)


def get_stats_ranked(server, summoner_id):
    url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v2.5/league/by-summoner/' + summoner_id
    params = {
        'api_key': config.keys.league_of_legends
    }
    return send_request(url, params)


def run(m):
    input = get_input(m)
    if not input:
        return send_message(m, lang.errors.input, markup='HTML')

    input = input.lower().replace(' ', '')
    
    global server
    server = None

    if not input:
        return send_message(m, lang.errors.results, markup='HTML')

    server = get_server(m)
    if not server:
        return send_message(m, lang.errors.results, markup='HTML')
    summoner = get_summoner(server, input)
    if not summoner:
        return send_message(m, lang.errors.results, markup='HTML')

    stats = get_stats(server, str(summoner[input]['id']))

    if not stats:
        return send_message(m, 'results')
    summoner_icon = get_summoner_icon(server, summoner, input)
    if not summoner_icon:
        return send_message(m, lang.errors.unknown, markup='HTML')

    try:
        ranked = get_stats_ranked(server, str(summoner[input]['id']))
    except:
        ranked = None

    text = summoner[input]['name']
    if summoner[input]['summonerLevel'] != 30:
        text += ' (Lv: ' + str(summoner[input]['summonerLevel']) + ')'

    if '30' in str(summoner[input]['summonerLevel']):
        if not ranked:
            text += '\n\nUnranked'
        else:
            if ranked[str(summoner[input]['id'])][0]['queue'] == 'RANKED_SOLO_5x5':
                i = 0
                found = False
                while not found:
                    if str(ranked[str(summoner[input]['id'])][0]['entries'][i]['playerOrTeamId']) != str(
                            summoner[input]['id']):
                        i += 1
                    else:
                        info = ranked[str(summoner[input]['id'])][0]['entries'][i]
                        found = True

                text += '\n\nRanked games:'
                text += '\n\tLeague: ' + ranked[str(summoner[input]['id'])][0]['tier'].title() + ' ' + info[
                    'division'] + ' (' + str(info['leaguePoints']) + 'LP)'
                text += '\n\tWins/Loses: ' + str(info['wins']) + '/' + str(info['losses']) + ' (' + str(
                    int((float(info['wins']) / (float(info['wins']) + float(info['losses']))) * 100)).replace('.',
                                                                                                              '\'') + '%)'
    text += '\n\nNormal games:'
    for summary in stats['playerStatSummaries']:
        if summary['playerStatSummaryType'] == 'Unranked':
            text += '\n\t5vs5 Wins: ' + str(summary['wins'])
        elif summary['playerStatSummaryType'] == 'Unranked3x3':
            text += '\n\t3vs3 Wins: ' + str(summary['wins'])
        elif summary['playerStatSummaryType'] == 'AramUnranked5x5':
            text += '\n\tARAM Wins: ' + str(summary['wins'])

    photo = download(summoner_icon)

    if photo:
        send_photo(m, photo, text)
    else:
        send_message(m, text)
