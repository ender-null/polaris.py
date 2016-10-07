from polaris.utils import get_input, get_coords, send_request, download, remove_html


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            self.bot.lang.plugins.weather.commands.weather.command: {
                'friendly': self.bot.lang.plugins.weather.commands.weather.friendly,
                'parameters': self.bot.lang.plugins.weather.commands.weather.parameters,
            },
            self.bot.lang.plugins.weather.commands.forecast.command: {
                'friendly': self.bot.lang.plugins.weather.commands.forecast.friendly,
                'parameters': self.bot.lang.plugins.weather.commands.forecast.parameters,
                'hidden': True
            }
        }
        self.description = self.bot.lang.plugins.help.description

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        if not input:
            return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

        lat, lon, locality, country = get_coords(input)

        url = 'http://api.wunderground.com/api/%s/webcams/conditions/forecast/q/%s,%s.json' % (
            self.bot.config.api_keys.weather_underground, lat, lon)

        data = send_request(url)

        try:
            weather = data.current_observation
            forecast = data.forecast.simpleforecast.forecastday
            webcams = data.webcams
        except:
            return self.bot.send_message(m, self.bot.lang.errors.no_results)

        title = self.bot.lang.plugins.weather.strings.title % (locality, country)

        temp = weather.temp_c
        feelslike = ""
        if (float(weather.feelslike_c) - float(weather.temp_c)) > 0.001:
            feelslike = self.bot.lang.plugins.weather.strings.feelslike % weather.feelslike_c
        weather_string = weather.weather.title()
        weather_icon = (self.get_weather_icon(weather.icon))
        humidity = weather.relative_humidity
        wind = weather.wind_kph

        if self.bot.lang.plugins.weather.commands.weather.command in m.content:
            message = u'\n%sºC%s - %s %s\n💧 %s | 🌬 %s km/h' % (
                temp, feelslike, weather_string, weather_icon, humidity, wind)
            try:
                photo_url = webcams[0].CURRENTIMAGEURL
                photo = download(photo_url)
            except Exception as e:
                photo = None
            
            if photo:
                return self.bot.send_message(m, photo, 'photo', extra={'caption': message})
            else:
                return self.bot.send_message(m, title + message, 'text', extra={'format': 'HTML'})

        elif self.bot.lang.plugins.weather.commands.forecast.command in m.content:
            message = self.bot.lang.plugins.weather.strings.titleforecast % (locality, country)
            for day in forecast:
                weekday = day.date.weekday
                temp = day.low.celsius
                temp_max = day.high.celsius
                weather_string = day.conditions.title()
                weather_icon = (self.get_weather_icon(day.icon))
                message += u'\n • <b>%s</b>: %s-%sºC - %s %s' % (weekday, temp, temp_max, weather_string, weather_icon)

            return self.bot.send_message(m, message, extra={'format': 'HTML'})

    @staticmethod
    def get_weather_icon(icon):
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
