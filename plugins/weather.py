from core.utils import *

commands = [
    ('/weather', ['location']),
    ('/forecast', ['location'])
]
description = 'Returns the current temperature and weather conditions for a specified location.'
shortcut = '/w '

def get_icon(icon):
    weather_emoji = {}
    if icon[:4] == 'nt_':
        weather_emoji['clear'] = u'☀️'
        weather_emoji['sunny'] = u'☀️'
        icon = icon.lstrip('nt_')
    else:
        weather_emoji['clear'] = u'🌙'
        weather_emoji['sunny'] = u'🌙'
    weather_emoji['chancesnow'] = u'❄️'
    weather_emoji['chanceflurries'] = u'❄️'
    weather_emoji['chancerain'] = u'🌧'
    weather_emoji['chancesleet'] = u'🌧'
    weather_emoji['chancetstorms'] = u'🌩'
    weather_emoji['cloudy'] = u'☁️'
    weather_emoji['flurries'] = u'❄️'
    weather_emoji['fog'] = u'🌫'
    weather_emoji['hazy'] = u'🌫'
    weather_emoji['mostlycloudy'] = u'🌥'
    weather_emoji['mostlycloudy'] = u'🌤'
    weather_emoji['partlycloudy'] = u'⛅️'
    weather_emoji['partlysunny'] = u'⛅️'
    weather_emoji['sleet'] = u'🌧'
    weather_emoji['rain'] = u'🌧'
    weather_emoji['sleet'] = u'🌧'
    weather_emoji['snow'] = u'❄️'
    weather_emoji['tstorms'] = u'⛈'

    return weather_emoji[icon]


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    lat, lon, locality, country = get_coords(input)

    url = 'http://api.wunderground.com/api/{0}/webcams/conditions/forecast/q/{1},{2}.json'.format(config.keys.weather,
                                                                                                  lat, lon)
    jstr = requests.get(url)

    if jstr.status_code != 200:
        return send_message(m, '%s\n%s' % (lang.errors.connection, jstr.text))

    weather = json.loads(jstr.text)['current_observation']
    forecast = json.loads(jstr.text)['forecast']['simpleforecast']['forecastday']
    webcams = json.loads(jstr.text)['webcams']

    title = '*Weather for '

    message = locality + ' \(' + country + '):*'
    message += '\n' + str(weather['temp_c']) + u'ºC '
    if (float(weather['feelslike_c']) - float(weather['temp_c'])) > 0.001:
        message += '\(feels like ' + str(weather['feelslike_c']) + 'ºC)'
    message += ' - ' + str(weather['weather']).title() + ' ' + get_icon(weather['icon'])
    message += u'\n💧 ' + str(weather['relative_humidity']) + u' | 🌬 ' + str(weather['wind_kph']) + ' km/h'

    simpleforecast = '\n\n*Forecast: *\n'
    for day in forecast:
        simpleforecast += '\t*{0}*: {1}-{2}ºC - {4}\n'.format(day['date']['weekday'], day['low']['celsius'],
                                                              day['high']['celsius'], day['conditions'],
                                                              get_icon(day['icon']))

    if get_command(m) == 'weather' or get_command(m) == 'w':
        if 'CURRENTIMAGEURL' in webcams[0]:
            photo_url = webcams[0]['CURRENTIMAGEURL']
            photo = download(photo_url)
        else:
            photo = None

        if photo:
            send_photo(m, photo, remove_markdown(message))
        else:
            send_message(m, title + message, markup='Markdown')

    elif get_command(m) == 'forecast':
        send_message(m, title + message + simpleforecast, markup='Markdown')
