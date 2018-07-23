from polaris.utils import get_input, is_command, get_coords, get_streetview, send_request, download, remove_html


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans['plugins']['weather']['commands']
        self.description = self.bot.trans['plugins']['weather']['description']

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans['errors']['missing_parameter'], extra={'format': 'HTML'})

        lat, lon, locality, country = get_coords(input)

        url = 'http://api.wunderground.com/api/%s/webcams/conditions/forecast/q/%s,%s.json' % (
            self.bot.config['api_keys']['weather_underground'], lat, lon)

        data = send_request(url)

        try:
            weather = data.current_observation
            forecast = data.forecast.simpleforecast.forecastday
            webcams = data.webcams
        except:
            return self.bot.send_message(m, self.bot.trans['errors']['no_results'])

        title = self.bot.trans['plugins']['weather']['strings']['title'] % (locality, country)
        temp = weather.temp_c
        feelslike = ""
        try:
            if (float(weather.feelslike_c) - float(weather.temp_c)) > 0.001:
                feelslike = self.bot.trans['plugins']['weather']['strings']['feelslike'] % weather.feelslike_c
        except:
            pass

        # weather_string = weather.weather.title()
        weather_string = self.bot.trans['plugins']['weather']['strings'][weather.icon]
        weather_icon = (self.get_weather_icon(weather.icon))
        humidity = weather.relative_humidity
        wind = format(float(weather.wind_kph) / 3.6, '.1f')

        if is_command(self, 1, m.content):
            message = u'%s\n%s %s%s\n🌡%sºC 💧%s 🌬%s m/s' % (
                remove_html(title), weather_icon, weather_string, feelslike, temp, humidity, wind)
            try:
                photo = get_streetview(lat, lon, self.bot.config['api_keys']['google_developer_console'])
            except Exception as e:
                print(e)
                photo = None

            if photo:
                return self.bot.send_message(m, photo, 'photo', extra={'caption': message})
            else:
                return self.bot.send_message(m, message, 'text', extra={'format': 'HTML'})

        elif is_command(self, 2, m.content):
            message = self.bot.trans['plugins']['weather']['strings']['titleforecast'] % (locality, country)
            for day in forecast:
                weekday = self.bot.trans['plugins']['weather']['strings'][day.date.weekday.lower()][:3]
                temp = day.low.celsius
                temp_max = day.high.celsius
                # weather_string = day.conditions.title()
                weather_string = self.bot.trans['plugins']['weather']['strings'][day.icon]
                weather_icon = (self.get_weather_icon(day.icon))
                message += u'\n • <b>%s</b>: 🌡 %s-%sºC %s %s' % (weekday, temp, temp_max, weather_icon, weather_string)

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
            weather_emoji['mostlycloudy'] = u'🌤'
            weather_emoji['partlycloudy'] = u'⛅️'
            weather_emoji['partlysunny'] = u'⛅️'
            weather_emoji['sleet'] = u'🌧'
            weather_emoji['rain'] = u'🌧'
            weather_emoji['sleet'] = u'🌧'
            weather_emoji['snow'] = u'❄️'
            weather_emoji['tstorms'] = u'⛈'

        return weather_emoji[icon]
