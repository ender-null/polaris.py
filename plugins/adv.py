from __main__ import *
from utilies import *
from bs4 import BeautifulSoup

commands = [
	'^adv',
	'^ascodevida'
]
description = 'Returns a random Hot Sick, Rude, Offensive & Politically Incorrect joke from [Sickipedia](http://sickipedia.org).'
typing = True

def action(msg):
	url = 'http://www.ascodevida.com/aleatorio'
	
	jstr = requests.get(url)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	soup = BeautifulSoup(jstr.text, 'lxml')

	text = soup.find(class_='advlink').get_text()
	text = text.replace('<br/>','\n')
	text = text.replace('\t','')
	
	core.send_message(msg.chat.id, text, parse_mode="Markdown")
