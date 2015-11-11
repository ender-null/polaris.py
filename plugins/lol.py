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
typing = True

def get_server(msg):
	if re.compile(config['command_start'] + 'br').search(msg.text):
		return 'br'
	elif re.compile(config['command_start'] + 'eune').search(msg.text):
		return 'eune'
	elif re.compile(config['command_start'] + 'kr').search(msg.text):
		return 'kr'
	elif re.compile(config['command_start'] + 'lan').search(msg.text):
		return 'lan'
	elif re.compile(config['command_start'] + 'las').search(msg.text):
		return 'las'
	elif re.compile(config['command_start'] + 'na').search(msg.text):
		return 'na'
	elif re.compile(config['command_start'] + 'oce').search(msg.text):
		return 'oce'
	elif re.compile(config['command_start'] + 'ru').search(msg.text):
		return 'ru'
	elif re.compile(config['command_start'] + 'tr').search(msg.text):
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
		params = params,
	)
	if res.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(res.status_code), parse_mode="Markdown")
	return json.loads(res.text)

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
		params = params,
	)
	if res.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(res.status_code), parse_mode="Markdown")
	return json.loads(res.text)
	
def get_stats_ranked(server, summoner_id, summoner_name):
	url = 'https://' + server + '.api.pvp.net//api/lol/' + server + '/v2.5/league/by-summoner/' + summoner_id
	params = {
		'api_key': config['api']['league_of_legends']
	}
	res = requests.get(
		url,
		params = params,
	)
	if res.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(res.status_code), parse_mode="Markdown")
	return json.loads(res.text)

def action(msg):
	input = get_input(msg.text)
	
	if not input:
		doc = get_doc(commands, parameters, description)
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	else:
		input = input.lower().replace(' ', '')
	
	server = get_server(msg)
	summoner = get_summoner(server, input)
	stats = get_stats(server, str(summoner[input]['id']), input)
	summoner_icon = get_summoner_icon(server, summoner, input)
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
		if ranked == None:
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
				text += '\n\tWins/Loses: ' + str(info['wins']) + '/' + str(info['losses']) + ' (' + str(int(( float(info['wins']) / (float(info['wins']) + float(info['losses'])) ) * 100)).replace('.','\'') + '%)'
			
	#core.send_message(msg.chat.id, text, parse_mode="Markdown")
	download_and_send(msg.chat.id, summoner_icon, 'photo', text)