from core.utils import *

commands = [
    ('/oweather', ['location'])
]
description = 'Returns the current temperature and weather conditions for a specified location. Uses Open Weather Map.'
shortcut = '/ow'
hidden = True

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


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    lat, lon, locality, country = get_coords(input)

    url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'lat': lat,
        'lon': lon,
        'units': 'metric',
        'appid': config.keys.openweathermap
    }

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        send_alert('%s\n%s' % (lang.errors.connection, jstr.text))
        return send_message(m, lang.errors.connection)

    weather = json.loads(jstr.text)

    if weather['cod'] == '404':
        return send_message(m, lang.errors.results)

    message = 'Weather for <b>' + locality + ' (' + country + ')</b>:'
    message += '\n' + str(int(weather['main']['temp'])) + u'ºC - ' + str(
        weather['weather'][0]['description']).title() + ' ' + get_icon(weather['weather'][0]['icon'])
    message += u'\n💧 ' + str(weather['main']['humidity']) + u'% | 🌬 ' + str(
        int(weather['wind']['speed'] * 3.6)) + ' km/h'

    send_message(m, message, markup='HTML')
