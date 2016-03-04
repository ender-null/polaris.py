from core.utils import *
from bs4 import BeautifulSoup

commands = [
    ('/joke', [])
]
description = 'Returns a random Hot Sick, Rude, Offensive & Politically Incorrect joke from Sickipedia.'


def run(m):
    url = 'http://www.sickipedia.org/random'

    jstr = requests.get(url)
    
    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)
        
    soup = BeautifulSoup(jstr.text, 'lxml')

    text = soup.find(itemprop='text').get_text()
    text = text.replace('<br/>', '\n')
    text = text.replace('\t', '')

    send_message(m, text, markup ='Markdown', preview = False)
