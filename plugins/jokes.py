from utilies import *
from bs4 import BeautifulSoup

commands = [
	'^joke',
	'^sp',
	'^sickipedia'
]
description = 'Returns a random Hot Sick, Rude, Offensive & Politically Incorrect joke from [Sickipedia](http://sickipedia.org).'
typing = True

def action(msg):
	url = 'http://www.sickipedia.org/random'
	
	jstr = requests.get(url)
		
	if jstr.status_code != 200:
		return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	soup = BeautifulSoup(jstr.text, 'lxml')

	text = soup.find(itemprop='text').get_text()
	text = text.replace('<br/>','\n')
	text = text.replace('\t','')
	
	send_message(msg['chat']['id'], text, parse_mode="Markdown")
