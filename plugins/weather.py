# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *
from random import randint

doc = config['command_start'] + 'weather *[location]*\nReturns the current temperature and weather conditions for a specified location.'

triggers = {
	'^' + config['command_start'] + 'weather',
	'^' + config['command_start'] + 'w '
}

typing = True

def get_icon(weather_icon):
	weather_emoji = {}
	weather_emoji['01'] = u'☀'
	weather_emoji['02'] = u'⛅'
	weather_emoji['03'] = u'☁'
	weather_emoji['04'] = u'☁'
	weather_emoji['09'] = u'☔'
	weather_emoji['10'] = u'☔'
	weather_emoji['11'] = u'⚡'
	weather_emoji['13'] = u'❄'
	weather_emoji['50'] = u'💨'
	
	return weather_emoji[weather_icon[:2]]

def action(msg):
	input = get_input(msg.text)
		
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")	
	
	weather_url = 'http://api.openweathermap.org/data/2.5/weather'
	weather_params = {
		'q': input,
		'units': 'metric',
		'appid': config['api']['openweathermap']
	}
	
	weather_jstr = requests.get(
		weather_url,
		params = weather_params,
	)
		
	if weather_jstr.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(weather_jstr.status_code))
	
	weather_jdat = json.loads(weather_jstr.text)

	if weather_jdat['cod'] == '404':
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['results'])
		
		
	photo_url = 'https://maps.googleapis.com/maps/api/streetview'
	photo_params = {
		'size': '640x320',
		'location': str(weather_jdat['coord']['lat']) + ',' + str(weather_jdat['coord']['lon']),
		'pitch': randint(0, 16),
		'heading': randint(0, 360),
		'key': config['api']['googledev']
	}

	message = 'Weather for ' + weather_jdat['name'] + ' (' + weather_jdat['sys']['country'] + ')'
	message += '\n' + str(int(weather_jdat['main']['temp'])) + u'ºC - ' + str(weather_jdat['weather'][0]['description']).title() + ' ' +  get_icon(weather_jdat['weather'][0]['icon'])
	message += u'\n💧 ' + str(weather_jdat['main']['humidity']) + u'% | 💨 ' + str(weather_jdat['wind']['speed']) + ' B'
	
	download_and_send(msg.chat.id, photo_url, 'photo', params=photo_params, caption=message)