from core.utils import *

commands = [
    ('/accuweather', ['location']),
    ('/accuforecast', ['location'])
]
description = 'Returns the current temperature and weather conditions for a specified location. Uses AccuWeather.'

def get_icon(icon):
    weather_emoji = {}
    weather_emoji['1'] = u'☀️'
    weather_emoji['2'] = u'☀️'
    weather_emoji['3'] = u'☀️'
    weather_emoji['4'] = u'☀️'
    weather_emoji['5'] = u'☀️'
    weather_emoji['6'] = u'☀️'
    weather_emoji['7'] = u'☀️'
    weather_emoji['8'] = u'☀️'
    weather_emoji['11'] = u'☀️'
    weather_emoji['12'] = u'☀️'
    weather_emoji['13'] = u'☀️'
    weather_emoji['14'] = u'☀️'
    weather_emoji['15'] = u'☀️'
    weather_emoji['16'] = u'☀️'
    weather_emoji['17'] = u'☀️'
    weather_emoji['18'] = u'☀️'
    weather_emoji['19'] = u'☀️'
    weather_emoji['20'] = u'☀️'
    weather_emoji['21'] = u'☀️'
    weather_emoji['22'] = u'☀️'
    weather_emoji['23'] = u'☀️'
    weather_emoji['24'] = u'☀️'
    weather_emoji['25'] = u'☀️'
    weather_emoji['26'] = u'☀️'
    weather_emoji['27'] = u'☀️'
    weather_emoji['28'] = u'☀️'
    weather_emoji['29'] = u'☀️'
    weather_emoji['30'] = u'☀️'
    weather_emoji['31'] = u'☀️'
    weather_emoji['32'] = u'☀️'
    weather_emoji['33'] = u'☀️'
    weather_emoji['34'] = u'☀️'
    weather_emoji['35'] = u'☀️'
    weather_emoji['36'] = u'☀️'
    weather_emoji['37'] = u'☀️'
    weather_emoji['38'] = u'☀️'
    weather_emoji['39'] = u'☀️'
    weather_emoji['40'] = u'☀️'
    weather_emoji['41'] = u'☀️'
    weather_emoji['42'] = u'☀️'
    weather_emoji['43'] = u'☀️'
    weather_emoji['44'] = u'☀️'

    return weather_emoji[icon]

def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    lat, lon, locality, country = get_coords(input)
    
    # Get location code.
    url = 'http://api.accuweather.com/locations/v1/cities/geoposition/search.json?q={1}, {2}&apikey={0}'.format(config.keys.weather, lat, lon)
    jstr = requests.get(url)

    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)
    
    location = json.loads(jstr.text)['Key']
    
    # Gets weather and photo for the location code.
    url = 'http://api.accuweather.com/currentconditions/v1/{1}.json?apikey={0}&getphotos=true&details=true'.format(config.keys.weather, location)
    jstr = requests.get(url)

    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)
    
    weather = json.loads(jstr.text)
    
    # Gets forecast for the location code.
    url = 'http://api.accuweather.com/forecasts/v1/daily/5day/{1}.json?apikey={0}&details=true&metric=true'.format(config.keys.weather, location)
    jstr = requests.get(url)
    
    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)
    
    forecast = json.loads(jstr.text)['DailyForecasts']

    title = '*Weather for '
    
    message = locality + ' \(' + country + '):*'
    message += '\n' + str(weather['Temperature']['Metric']['Value']) + u'ºC '
    if (float(weather['RealFeelTemperature']['Metric']['Value']) - float(weather['Temperature']['Metric']['Value'])) > 0.001:
        message += '\(feels like ' + str(weather['RealFeelTemperature']['Metric']['Value']) + 'ºC)'
    message += ' - ' + str(weather['WeatherText']).title() + ' ' + get_icon(str(weather['WeatherIcon']))
    message += u'\n💧 ' + str(weather['RelativeHumidity']) + u' | 🌬 ' + str(weather['Wind']['Speed']['Metric']['Value']) + ' km/h'
    
    simpleforecast = '\n\n*Forecast: *\n'
    for day in forecast:
        simpleforecast += '\t*{0}*: {1}-{2}ºC - {4} | {5} km/h\n'.format(day['Date'].split('T')[0], day['Temperature']['Minimum']['Value'], day['Temperature']['Maximum']['Value'], day['Day']['IconPhrase'], get_icon(str(day['Day']['Icon'])), day['Day']['Wind']['Speed']['Value'])
    
    if get_command(m) == 'accuweather':
        photo = download(weather['Photos'][0]['LandscapeLink'])
            
        if photo:
            send_photo(m, photo, remove_markdown(message))
        else:
            send_message(m, title + message, markup = 'Markdown')
            
    elif get_command(m) == 'accuforecast':
        send_message(m, title + message + simpleforecast, markup = 'Markdown')
