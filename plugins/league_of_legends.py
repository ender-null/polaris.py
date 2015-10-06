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

def action(msg):
	input = get_input(msg.text).lower().replace(' ', '')
	
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	if msg.text.startswith(config.command_start + 'br'):
		server = 'br'
	elif msg.text.startswith(config.command_start + 'eune'):
		server = 'eune'
	elif msg.text.startswith(config.command_start + 'kr'):
		server = 'kr'
	elif msg.text.startswith(config.command_start + 'lan'):
		server = 'lan'
	elif msg.text.startswith(config.command_start + 'las'):
		server = 'las'
	elif msg.text.startswith(config.command_start + 'na'):
		server = 'na'
	elif msg.text.startswith(config.command_start + 'oce'):
		server = 'oce'
	elif msg.text.startswith(config.command_start + 'ru'):
		server = 'ru'
	elif msg.text.startswith(config.command_start + 'tr'):
		server = 'tr'
	else:
		server = 'euw'

	params = {
		'api_key': config.apis['league_of_legends']
	}
	
	
		
	summoner_url = 'https://' + server + '.api.pvp.net/api/lol/' + server + '/v1.4/summoner/by-name/' + input		
	summoner_res = requests.get(
		summoner_url,
		params = params,
	)
	if summoner_res.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(summoner_res.status_code), parse_mode="Markdown")
	summoner = json.loads(summoner_res.text)
	
	
	
	stats_url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v1.3/stats/by-summoner/' + str(summoner[input]['id']) + '/summary'
	stats_res = requests.get(
		stats_url,
		params = params,
	)
	if stats_res.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(stats_res.status_code), parse_mode="Markdown")
	stats = json.loads(stats_res.text)
	
	summoner_icon_url = 'http://ddragon.leagueoflegends.com/cdn/5.19.1/img/profileicon/'
	summoner_icon = summoner_icon_url + str(summoner[input]['profileIconId']) + '.png'
	
	try:
		ranked_url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v2.5/league/by-summoner/' + str(summoner[input]['id'])
		ranked_res = requests.get(
			ranked_url,
			params = params,
		)
		ranked = json.loads(ranked_res.text)
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
