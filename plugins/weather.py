# -*- coding: utf-8 -*-
from utilies import *
from random import randint


commands = [
    '^weather',
    '^w ',
    '^w$'
]

parameters = {('location', True)}

description = 'Returns the current temperature and weather conditions for a specified location.'
action = 'upload_photo'


def get_icon(weather_icon):
    weather_emoji = {}
    if weather_icon[2] == 'd':
        weather_emoji['01'] = u'☀️'
    else:
        weather_emoji['01'] = u'🌙'
    weather_emoji['02'] = u'⛅️'
    weather_emoji['03'] = u'☁️'
    weather_emoji['04'] = u'☁️'
    weather_emoji['09'] = u'🌧'
    weather_emoji['10'] = u'🌦'
    weather_emoji['11'] = u'⛈'
    weather_emoji['13'] = u'🌨'
    weather_emoji['50'] = u'🌫'

    return weather_emoji[weather_icon[:2]]


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    lat, lon, locality, country = get_coords(input)
    print lat
    print lon

    weather_url = 'http://api.openweathermap.org/data/2.5/weather'
    weather_params = {
        'lat': lat,
        'lon': lon,
        'units': 'metric',
        'appid': config['api']['openweathermap']
    }

    weather = send_request(weather_url, weather_params)
    if not weather:
        return send_error(msg, 'connection')

    if weather['cod'] == '404':
        return send_error(msg, 'results')

    photo_url = 'https://maps.googleapis.com/maps/api/streetview'
    photo_params = {
        'size': '640x320',
        'location': str(lat) + ',' + str(lon),
        'pitch': 16,
        'key': config['api']['googledev']
    }

    message = locality + ' (' + country + ')'
    message += '\n' + str(int(weather['main']['temp'])) + u'ºC - ' + str(weather['weather'][0]['description']).title() + ' ' + get_icon(weather['weather'][0]['icon'])
    message += u'\n💧 ' + str(weather['main']['humidity']) + u'% | 🌬 ' + str(int(weather['wind']['speed'] * 3.6)) + ' km/h'

    photo = download(photo_url, params=photo_params)
    if photo:
        if not send_photo(msg['chat']['id'], photo, caption=message):
            send_error(msg, 'unknown')
    else:
        send_error(msg, 'download')
