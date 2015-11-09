# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *

commands = [
	'^torrent',
	'^t ',
	'^kickass'
]
parameters = (
	('query', True),
)
description = 'Search Kickass Torrents. Results may be NSFW.'
typing = True

def get_category_icon(category):
	if category == 'Anime':
		return u'🎌'
	elif category == 'Applications':
		return u'💻'
	elif category == 'Books':
		return u'📔'
	elif category == 'Games':
		return u'🎮'
	elif category == 'Movies':
		return u'🎥'
	elif category == 'Music':
		return u'🎵'
	elif category == 'TV':
		return u'📺'
	elif category == 'XXX':
		return u'🔞'
	else:
		return u'❔'
		
def get_size(number):
	size = ''
	unit = 0
	
	units = [
		'B',
		'KB',
		'MB',
		'GB',
		'TB'
	]
	
	while (number > 1024):
		number = number/1024
		unit = unit + 1
		
	return str(number) + ' ' + units[unit]

def action(msg):
	input = get_input(msg.text)
		
	if not input:
		doc = get_doc(commands, parameters, description)
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
		
	url = 'http://kat.cr/json.php'
	params = {
		'q': input
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	jdat = json.loads(jstr.text)

	if jdat['total_results'] == 0:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['results'])
	
	limit = 6
	if len(jdat['total_results']) < limit:
		limit = len(jdat['total_results'])


	for v in jdat['list']:
		if v['seeds'] == 0:
			del v

	if len(jdat['list']) == 0:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['results'])

	message = '*Kickass search*: "_' + input + '_"\n\n'
	for i in range(0, limit):
		message += get_category_icon(jdat['list'][i]['category']) + ' [' + delete_markup(jdat['list'][i]['title']) + '](' + delete_markup(jdat['list'][i]['torrentLink']) + ')'
		if jdat['list'][i]['verified'] == 0:
			message += u' ❗️'
		message += u'\n📦 ' + get_size(jdat['list'][i]['size']) + ' | '
		message += u'🌱 ' + str(jdat['list'][i]['seeds'])
		message += u' | 👤 ' + str(jdat['list'][i]['peers'])
		message += u' | 👍 ' + str(jdat['list'][i]['votes']) + '\n\n'

	message = message.replace('&amp;', '&')
	
	core.send_message(msg.chat.id, message, parse_mode="Markdown")
