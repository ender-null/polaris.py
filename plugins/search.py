from __main__ import *
from utilies import *

doc = config.command_start + 'search *[query]*\nThis command performs a Google search for the given query. Safe search is enabled by default; use *' + config.command_start + 'gnsfw* to get potentially NSFW results'

triggers = {
	'^' + config.command_start + 'search',
	'^' + config.command_start + 'google',
	'^' + config.command_start + 'g',
	'^' + config.command_start + 'gnsfw'
}


def action(msg):
	input = get_input(msg.text)
		
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
		
	url = 'http://ajax.googleapis.com/ajax/services/search/web'
	params = {
		'v': '1.0',
		'rsz': 6,
		'safe': 'active',
		'q': input
	}
	
	if msg.text.startswith(config.command_start + 'insfw'):
		del params['safe']
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	jdat = json.loads(jstr.text)

	if jdat['responseData']['results'] < 1:
		return core.send_message(msg.chat.id, config.locale.errors['results'], parse_mode="Markdown")
	
	text = '*Search*: "_' + input + '_"\n\n'
	for i in range(0, len(jdat['responseData']['results'])):
		result_url = jdat['responseData']['results'][i]['unescapedUrl']
		result_title = jdat['responseData']['results'][i]['titleNoFormatting']
		text += result_title + '\n' + result_url + '\n\n' 
	
	core.send_message(msg.chat.id, text, disable_web_page_preview=True, parse_mode="Markdown")

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
}