from __main__ import *
from utilies import *

commands = [
	'^currency',
	'^cash',
	'^c '
]
parameters = (
	('to', True),
	('from', True),
	('ammount', False),
)
description = 'Convert an amount from one currency to another.'
typing = True
hidden = True

def action(msg):
	input = get_input(msg['text'])

	if not input:
		doc = get_doc(commands, parameters, description)
		return send_message(msg['chat']['id'], doc, parse_mode="Markdown")	
			
	url = 'http://www.google.com/finance/converter'
	params = {
		'size': '640x320',
		'markers': 'color:red|label:X|' + str(lat) + ',' + str(lon),
		'key': config['api']['googledev']
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['connection'].format(jstr.status_code))
	
	jdat = json.loads(jstr.text)
	
	'''
	local from = first_word(input):upper()
	local to = first_word(input, 2):upper()
	local amount = first_word(input, 3)
	local result

	if not tonumber(amount) then
		amount = 1
		result = 1
	end

	if from ~= to then

		local url = url .. '?from=' .. from .. '&to=' .. to .. '&a=' .. amount

		local str, res = HTTP.request(url)
		if res ~= 200 then
			return send_msg(msg, config.locale.errors.connection)
		end

		local str = str:match('<span class=bld>(.*) %u+</span>')
		if not str then return send_msg(msg, config.locale.errors.results) end
		result = string.format('%.2f', str)

	end

	local message = amount .. ' ' .. from .. ' = ' .. result .. ' ' .. to
	'''
	
	#send_location(msg['chat']['id'], lat, lon)