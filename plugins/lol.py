# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *


commands = [
    '^stats',
    '^br ',
    '^eune ',
    '^euw ',
    '^kr ',
    '^lan ',
    '^las ',
    '^na ',
    '^oce ',
    '^ru ',
    '^tr '
]

parameters = (
    ('summoner', True),
)

description = 'Gets stats from League of Legends summoner.'
action = 'upload_photo'


def get_server(msg):
    if get_command(msg['text']) == 'br':
        return 'br'
    elif get_command(msg['text']) == 'eune':
        return 'eune'
    elif get_command(msg['text']) == 'kr':
        return 'kr'
    elif get_command(msg['text']) == 'lan':
        return 'lan'
    elif get_command(msg['text']) == 'las':
        return 'las'
    elif get_command(msg['text']) == 'na':
        return 'na'
    elif get_command(msg['text']) == 'oce':
        return 'oce'
    elif get_command(msg['text']) == 'ru':
        return 'ru'
    elif get_command(msg['text']) == 'tr':
        return 'tr'
    else:
        return 'euw'


def get_summoner(server, input):
    url = 'https://' + server + '.api.pvp.net/api/lol/' + server + '/v1.4/summoner/by-name/' + input
    params = {
        'api_key': config['api']['league_of_legends']
    }
    res = requests.get(
        url,
        params=params,
    )
    if res.status_code != 200:
        return None
    return json.loads(res.text)
#   return send_request(url, params)


def get_summoner_icon(server, summoner, summoner_name):
    url = 'http://ddragon.leagueoflegends.com/cdn/5.19.1/img/profileicon/'
    return url + str(summoner[summoner_name]['profileIconId']) + '.png'


def get_stats(server, summoner_id, summoner_name):
    url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v1.3/stats/by-summoner/' + summoner_id + '/summary'
    params = {
        'api_key': config['api']['league_of_legends']
    }

    res = requests.get(
        url,
        params=params,
    )
    if res.status_code != 200:
        return send_error(msg, 'connection', res.status_code)
    return json.loads(res.text)
    #return send_request(url, params)


def get_stats_ranked(server, summoner_id, summoner_name):
    url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v2.5/league/by-summoner/' + summoner_id
    params = {
        'api_key': config['api']['league_of_legends']
    }
    res = requests.get(
        url,
        params=params,
    )
    if res.status_code != 200:
        return send_error(msg, 'connection', res.status_code)
    return json.loads(res.text)
    #return send_request(url, params)


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")
    else:
        input = input.lower().replace(' ', '')

    server = get_server(msg)
    if not server:
        return send_error(msg, 'results')
    summoner = get_summoner(server, input)
    if not summoner:
        return send_error(msg, 'unknown')
    stats = get_stats(server, str(summoner[input]['id']), input)
    if not stats:
        return send_error(msg, 'permission')
    summoner_icon = get_summoner_icon(server, summoner, input)
    if not summoner_icon:
        return send_error(msg, 'id')

    try:
        ranked = get_stats_ranked(server, str(summoner[input]['id']), input)
    except:
        ranked = None

    text = summoner[input]['name']
    text += '\nLevel: ' + str(summoner[input]['summonerLevel'])
    text += '\n\nNormal games:'
    for summary in stats['playerStatSummaries']:
        if summary['playerStatSummaryType'] == 'Unranked':
            text += '\n\t5vs5 Wins: ' + str(summary['wins'])
        elif summary['playerStatSummaryType'] == 'Unranked3x3':
            text += '\n\t3vs3 Wins: ' + str(summary['wins'])
        elif summary['playerStatSummaryType'] == 'AramUnranked5x5':
            text += '\n\tARAM Wins: ' + str(summary['wins'])

    if '30' in str(summoner[input]['summonerLevel']):
        if ranked is None:
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
        send_photo(msg['chat']['id'], photo, caption=text)
    else:
        send_error(msg, 'download')
