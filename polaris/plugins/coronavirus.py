import requests
from bs4 import BeautifulSoup

from polaris.utils import generate_command_help, get_input


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.coronavirus.commands
        self.description = self.bot.trans.plugins.coronavirus.description

    # Plugin action #
    def run(self, m):
        url = 'https://www.worldometers.info/coronavirus/'

        country = get_input(m, ignore_reply=False)
        if country:
            url += 'country/' + country.lower().lstrip()

        else:
            return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})

        res = requests.get(url)

        if res.status_code != 200:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

        soup = BeautifulSoup(res.text, 'html.parser')

        try:
            counters = soup.findAll(class_='maincounter-number')
            cases = counters[0].find('span').get_text()
            deaths = counters[1].find('span').get_text()
            recovered = counters[2].find('span').get_text()

            text = None
            if country:
                text = self.bot.trans.plugins.coronavirus.strings.input_result % (
                    country.title(), cases, deaths, recovered)
            else:
                text = self.bot.trans.plugins.coronavirus.strings.result % (
                    cases, deaths, recovered)

            text += '\n\n<a href="%s">%s</a>' % (
                url, self.bot.trans.plugins.coronavirus.strings.source)

            self.bot.send_message(
                m, text, extra={'format': 'HTML', 'preview': False})

        except Exception as e:
            self.bot.send_message(
                m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})
