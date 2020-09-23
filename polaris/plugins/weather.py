import logging

from DictObject import DictObject

from polaris.utils import (catch_exception, download, generate_command_help,
                           get_coords, get_input, get_streetview, is_command,
                           remove_html, send_request)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.weather.commands
        self.description = self.bot.trans.plugins.weather.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
            # return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        status, values = get_coords(input, self.bot)

        if status == 'ZERO_RESULTS' or status == 'INVALID_REQUEST':
            return self.bot.send_message(m, self.bot.trans.errors.api_limit_exceeded, extra={'format': 'HTML'})
        elif status == 'OVER_DAILY_LIMIT':
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})
        elif status == 'REQUEST_DENIED':
            return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

        lat, lon, locality, country = values

        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'APPID': self.bot.config.api_keys.open_weather,
            'lon': lon,
            'lat': lat,
            'units': 'metric',
            'lang': 'es'
        }

        data = send_request(url, params, bot=self.bot)
        logging.info(data)
        if not data or data.cod != 200:
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        title = self.bot.trans.plugins.weather.strings.title % (
            locality, country)
        # weather_string = weather.weather.title()
        #weather_string = str(self.bot.trans.plugins.weather.strings[data.weather.id])
        weather_string = data.weather[0].main
        weather_icon = self.get_weather_icon(data.weather[0].icon)
        temp = round(data.main.temp, 1)
        humidity = data.main.humidity
        wind = data.wind.speed
        feelslike = ''
        # try:
        #     temp_c = mc.Temp(data.main.temp, 'c')
        #     feelslike_c = round(mc.heat_index(temperature=temp_c, humidity=humidity), 1)
        #     if (float(feelslike_c) - float(data.main.temp)) > 0.001:
        #         feelslike = self.bot.trans.plugins.weather.strings.feelslike % feelslike_c
        # except:
        #     pass

        if is_command(self, 1, m.content):
            message = u'%s\n%s %s%s\n🌡%sºC 💧%s%% 🌬%s m/s' % (
                remove_html(title), weather_icon, weather_string, feelslike, temp, humidity, wind)
            try:
                photo = get_streetview(
                    lat, lon, self.bot.config.api_keys.google_developer_console)
            except Exception as e:
                catch_exception(e, self.bot)
                photo = None

            if photo:
                return self.bot.send_message(m, photo, 'photo', extra={'caption': message})
            else:
                return self.bot.send_message(m, message, extra={'format': 'HTML'})

        elif is_command(self, 2, m.content):
            return self.bot.send_message(m, self.bot.trans.errors.not_implemented, extra={'format': 'HTML'})
            # message = self.bot.trans.plugins.weather.strings.titleforecast % (locality, country)
            # for day in forecast:
            #     weekday = self.bot.trans.plugins.weather.strings[day.date.weekday.lower()][:3]
            #     temp = day.low.celsius
            #     temp_max = day.high.celsius
            #     # weather_string = day.conditions.title()
            #     weather_string = self.bot.trans.plugins.weather.strings[day.icon]
            #     weather_icon = (self.get_weather_icon(day.icon))
            #     message += u'\n • <b>%s</b>: 🌡 %s-%sºC %s %s' % (weekday, temp, temp_max, weather_icon, weather_string)

            # return self.bot.send_message(m, message, extra={'format': 'HTML'})

    @staticmethod
    def get_weather_icon(icon):
        weather_emoji = DictObject()
        if icon[2] == 'n':
            weather_emoji['01'] = u'🌙'
        else:
            weather_emoji['01'] = u'☀️'
        weather_emoji['02'] = u'⛅️'
        weather_emoji['03'] = u'🌤'
        weather_emoji['04'] = u'☁️'
        weather_emoji['09'] = u'🌧'
        weather_emoji['10'] = u'🌧'
        weather_emoji['11'] = u'⛈'
        weather_emoji['13'] = u'❄️'
        weather_emoji['50'] = u'🌫'
        return weather_emoji[icon[:2]]
