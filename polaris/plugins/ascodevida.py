import requests
from bs4 import BeautifulSoup


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            '/adv': {}
        }
        self.description = 'ADV aleatorios de Asco de vida.'

    # Plugin action #
    def run(self, m):
        url = 'http://www.ascodevida.com/aleatorio'
        res = requests.get(url)

        if res.status_code != 200:
            send_alert('%s\n%s' % (lang.errors.connection, res.text))
            return self.bot.send_message(m, self.bot.lang.errors.connection_error, extra={'format': 'HTML'})
        
        soup = BeautifulSoup(res.text, 'lxml')

        text = soup.find(class_='advlink').get_text()
        text = text.replace('<br/>', '\n')
        text = text.replace('ADV', '<b>ADV</b>')
        
        self.bot.send_message(m, text, extra={'format': 'HTML'})
