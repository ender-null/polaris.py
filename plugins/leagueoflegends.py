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
        elif get_command(m]) == 'na':
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


def get_summoner(server, input):
    url = 'https://' + server + '.api.pvp.net/api/lol/' + server + '/v1.4/summoner/by-name/' + input
    params = {
        'api_key': config.keys.league_of_legends
    }
    return send_request(url, params)


def get_summoner_icon(server, summoner, summoner_name):
    url = 'http://ddragon.leagueoflegends.com/cdn/6.2.1/img/profileicon/'
    return url + str(summoner[summoner_name]['profileIconId']) + '.png'


def get_stats(server, summoner_id):
    url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v1.3/stats/by-summoner/' + summoner_id + '/summary'
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
    global server
    server = None

    if not input:
        return send_message(m, 'No Results!')

    server = get_server(m)
    if not server:
        return send_message(m, 'No Results!')
    summoner = get_summoner(server, input)
    if not summoner:
        return send_message(m, 'No Results!')
        
    stats = get_stats(server, str(summoner[input]['id']))
    
    print(stats)
    
    if not stats:
        return send_error(m, 'results')
    summoner_icon = get_summoner_icon(server, summoner, input)
    if not summoner_icon:
        return send_message(m, 'Unknown Error!')

    try:
        ranked = get_stats_ranked(server, str(summoner[input]['id']))
    except:
        ranked = None

    text = summoner[input]['name'] + ' (Lv: ' + str(summoner[input]['summonerLevel']) + ')'
    text += '\n\nNormal games:'
    for summary in stats['playerStatSummaries']:
        if summary['playerStatSummaryType'] == 'Unranked':
            text += '\n\t5vs5 Wins: ' + str(summary['wins'])
        elif summary['playerStatSummaryType'] == 'Unranked3x3':
            text += '\n\t3vs3 Wins: ' + str(summary['wins'])
        elif summary['playerStatSummaryType'] == 'AramUnranked5x5':
            text += '\n\tARAM Wins: ' + str(summary['wins'])
    
    if '30' in str(summoner[input]['summonerLevel']):
        if not ranked:
            text += '\n\nUnranked'
        else:
            if ranked[str(summoner[input]['id'])][0]['queue'] == 'RANKED_SOLO_5x5':
                i = 0
                found = False
                while not found:
                    if str(ranked[str(summoner[input]['id'])][0]['entries'][i]['playerOrTeamId']) != str(summoner[input]['id']):
                        i += 1
                    else:
                        info = ranked[str(summoner[input]['id'])][0]['entries'][i]
                        found = True

                text += '\n\nRanked games:'
                text += '\n\tLeague: ' + ranked[str(summoner[input]['id'])][0]['tier'] + ' ' + info['division'] + ' (' + str(info['leaguePoints']) + 'LP)'
                text += '\n\tWins/Loses: ' + str(info['wins']) + '/' + str(info['losses']) + ' (' + str(int(( float(info['wins']) / (float(info['wins']) + float(info['losses']))) * 100)).replace('.', '\'') + '%)'

    photo = download(summoner_icon)

    if photo:
        send_photo(m, photo, text)
    else:
        send_message(m, text)
