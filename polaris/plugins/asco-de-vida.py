from bs4 import BeautifulSoup
import requests


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '/adv',
                'description': 'ADV aleatorios.'
            }
        ]
        self.description = 'ADV aleatorios de Asco de vida.'

    # Plugin action #
    def run(self, m):
        url = 'http://www.ascodevida.com/aleatorio'
        res = requests.get(url)

        if res.status_code != 200:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})
        
        soup = BeautifulSoup(res.text, 'html.parser')

        story = soup.find(class_='story')
        published = story.find(class_='pre').get_text()
        content = story.find(class_='advlink').get_text()
        content = content.replace('<br/>', '\n')
        content = content.replace('ADV', '<b>ADV</b>')

        text = '%s\n<i>%s</i>' % (content, published)
        
        self.bot.send_message(m, text, extra={'format': 'HTML'})
