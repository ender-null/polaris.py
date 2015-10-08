from __main__ import *
from utilies import *

doc = config.command_start + 'summoner *[summoner]*\nGets stats from summoner.'

triggers = {
	'^' + config.command_start + 'summoner',
	'^' + config.command_start + 'br',
	'^' + config.command_start + 'eune',
	'^' + config.command_start + 'euw',
	'^' + config.command_start + 'kr',
	'^' + config.command_start + 'lan',
	'^' + config.command_start + 'las',
	'^' + config.command_start + 'na',
	'^' + config.command_start + 'oce',
	'^' + config.command_start + 'ru',
	'^' + config.command_start + 'tr',
}

def get_server(msg):
	if msg.text.startswith(config.command_start + 'br'):
		return 'br'
	elif msg.text.startswith(config.command_start + 'eune'):
		return 'eune'
	elif msg.text.startswith(config.command_start + 'kr'):
		return 'kr'
	elif msg.text.startswith(config.command_start + 'lan'):
		return 'lan'
	elif msg.text.startswith(config.command_start + 'las'):
		return 'las'
	elif msg.text.startswith(config.command_start + 'na'):
		return 'na'
	elif msg.text.startswith(config.command_start + 'oce'):
		return 'oce'
	elif msg.text.startswith(config.command_start + 'ru'):
		return 'ru'
	elif msg.text.startswith(config.command_start + 'tr'):
		return 'tr'
	else:
		return 'euw'

def get_summoner(server, input):
	url = 'https://' + server + '.api.pvp.net/api/lol/' + server + '/v1.4/summoner/by-name/' + input		
	params = {
		'api_key': config.apis['league_of_legends']
	}
	res = requests.get(
		url,
		params = params,
	)
	if res.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(res.status_code), parse_mode="Markdown")
	return json.loads(res.text)

def get_summoner_icon(server, summoner, summoner_name):
	url = 'http://ddragon.leagueoflegends.com/cdn/5.19.1/img/profileicon/'
	return url + str(summoner[summoner_name]['profileIconId']) + '.png'
	
def get_stats(server, summoner_id, summoner_name):
	url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v1.3/stats/by-summoner/' + summoner_id + '/summary'
	params = {
		'api_key': config.apis['league_of_legends']
	}
	res = requests.get(
		url,
		params = params,
	)
	if res.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(res.status_code), parse_mode="Markdown")
	return json.loads(res.text)
	
def get_stats_ranked(server, summoner_id, summoner_name):
	url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v2.5/league/by-summoner/' + summoner_id
	params = {
		'api_key': config.apis['league_of_legends']
	}
	res = requests.get(
		url,
		params = params,
	)
	if res.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(res.status_code), parse_mode="Markdown")
	return json.loads(res.text)

def action(msg):
	input = get_input(msg.text).lower().replace(' ', '')
	
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	server = get_server(msg)
	summoner = get_summoner(server, input)
	stats = get_stats(server, str(summoner[input]['id']), input)
	summoner_icon = get_summoner_icon(server, summoner, input)
	
	try:
		ranked = get_stats_ranked(server, str(summoner[input]['id']), input)
	except:
		pass
	
	
	text = 'Name: ' + summoner[input]['name'] + '\n'
	text += 'Level: ' + str(summoner[input]['summonerLevel']) + '\n\n'
	for summary in stats['playerStatSummaries']:
		if summary['playerStatSummaryType'] == 'Unranked':
			text += '5vs5 wins: ' + str(summary['wins']) + '\n'
		elif summary['playerStatSummaryType'] == 'Unranked3x3':
			text += '3vs3 wins: ' + str(summary['wins']) + '\n'
		elif summary['playerStatSummaryType'] == 'AramUnranked5x5':
			text += 'ARAM wins: ' + str(summary['wins']) + '\n'
	
	if '30' in str(summoner[input]['summonerLevel']):
		if ranked[str(summoner[input]['id'])][0]['queue'] == 'RANKED_SOLO_5x5':
			i = 0
			found = False
			while not found:
				if str(ranked[str(summoner[input]['id'])][0]['entries'][i]['playerOrTeamId']) != str(summoner[input]['id']):
					i += 1
				else:
					info = ranked[str(summoner[input]['id'])][0]['entries'][i]
					found = True
			
			text += '\nRanked\n'
			text += 'League: ' + ranked[str(summoner[input]['id'])][0]['tier'] + ' ' + info['division'] + ' (' + str(info['leaguePoints']) + 'LP)\n'
			text += 'Wins/Loses: ' + str(info['wins']) + '/' + str(info['losses']) + '\n'
			text += 'Winrate: ' + str(int(( float(info['wins']) / (float(info['wins']) + float(info['losses'])) ) * 100)).replace('.','\'') + '%'
			
	#core.send_message(msg.chat.id, text, parse_mode="Markdown")
	download_and_send(msg.chat.id, summoner_icon, 'photo', text)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None,
}
