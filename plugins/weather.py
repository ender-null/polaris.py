# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *

doc = config['command_start'] + 'weather *[location]*\nReturns the current temperature and weather conditions for a specified location.'

triggers = {
	'^' + config['command_start'] + 'weather',
	'^' + config['command_start'] + 'w '
}

typing = True

def action(msg):
	input = get_input(msg.text)
		
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")	
	
	
	lat,lon = get_coords(input)
	if not lat or not lon:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['results'])
	
	url = 'http://api.openweathermap.org/data/2.5/weather'
	params = {
		#'lat': lat,
		#'lon': lon,
		'q': input,
		'appid': config['api']['openweathermap']
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(jstr.status_code))
	
	jdat = json.loads(jstr.text)

	if jdat['cod'] == '404':
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['results'])

	message = '*' + jdat['name'] + ', ' + jdat['sys']['country'] + '*'
	message += '\nWeather: ' + str(jdat['weather'][0]['description'])
	message += '\nTemperature: _' + str(int(jdat['main']['temp'] - 273.15)) + u'ºC_'
	message += '\nHumidity: _' + str(jdat['main']['humidity']) + '%_'
	message += '\nWind speed: _' + str(jdat['wind']['speed']) + '_'
	
	core.send_message(msg.chat.id, message, parse_mode="Markdown")
