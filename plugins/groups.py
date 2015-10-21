from __main__ import *
from utilies import *

triggers = {
	'^' + config['command_start'] + 'add',
	'^' + config['command_start'] + 'remove',
	'^' + config['command_start'] + 'set',
	'^' + config['command_start'] + 'list',
	'^' + config['command_start'] + 'info',
	'^' + config['command_start'] + 'broadcast',
	'^' + config['command_start'] + 'kick',
	'^' + config['command_start'] + 'rules',
	'^' + config['command_start'] + 'promote',
	'^' + config['command_start'] + 'demote',
	'^' + config['command_start'] + 'join',
}

def action(msg):			
	input = get_input(msg.text)
	
	message = locale['default']['errors']['argument']
	
	if msg.from_user.id not in config['admin']:
		return core.send_message(msg.chat.id, locale[get_locale(msg.chat.id)]['errors']['permission'])
	
	if msg.text.startswith(config['command_start'] + 'add'):
		if msg.chat.type == 'group':
			if not str(msg.chat.id) in groups:
				if len(first_word(msg.chat.title)) == 1:
					realm = first_word(msg.chat.title)
					title = all_but_first_word(msg.chat.title)
				else:
					realm = '*'
					title = msg.chat.title
			
				groups[str(msg.chat.id)] = {}
				groups[str(msg.chat.id)]['link'] = ''
				groups[str(msg.chat.id)]['realm'] = realm
				groups[str(msg.chat.id)]['title'] = title
				groups[str(msg.chat.id)]['description'] = 'Group added by ' + msg.from_user.first_name
				groups[str(msg.chat.id)]['rules'] = ''
				groups[str(msg.chat.id)]['locale'] = 'default'
				groups[str(msg.chat.id)]['special'] = None
				groups[str(msg.chat.id)]['hide'] = False
				groups[str(msg.chat.id)]['mods'] = {}
				groups[str(msg.chat.id)]['mods'][msg.from_user.id] = msg.from_user.first_name
			
				save_json('groups.json', groups)
				
				message = 'Group added.'
			else:
				message = 'Already added.'
		else:
			message = 'You can only add chat groups.'
		
	elif msg.text.startswith(config['command_start'] + 'remove'):
		del groups[str(msg.chat.id)]
		message = 'Group removed'
		
	elif msg.text.startswith(config['command_start'] + 'set'):
		if first_word(input) == 'link':
			groups[str(msg.chat.id)]['link'] = all_but_first_word(input)
			message = 'Updated invite link of ' + groups[str(msg.chat.id)]['title'] + '.'
			
		elif first_word(input) == 'realm':
			groups[str(msg.chat.id)]['realm'] = all_but_first_word(input)
			message = 'Updated realm of ' + groups[str(msg.chat.id)]['title'] + '.'
			
		elif first_word(input) == 'description':
			groups[str(msg.chat.id)]['description'] = all_but_first_word(input)
			message = 'Updated description of ' + groups[str(msg.chat.id)]['title'] + '.'
			
		elif first_word(input) == 'rules':
			groups[str(msg.chat.id)]['rules'] = all_but_first_word(input)
			message = 'Updated rules of ' + groups[str(msg.chat.id)]['title'] + '.'
			
		elif first_word(input) == 'locale':
			groups[str(msg.chat.id)]['locale'] = all_but_first_word(input)
			message = 'Updated locale of ' + groups[str(msg.chat.id)]['title'] + '.'
			
		elif first_word(input) == 'hide':
			groups[str(msg.chat.id)]['hide'] = all_but_first_word(input)
			message = 'Updated hide status of ' + groups[str(msg.chat.id)]['title'] + '.'
			
		save_json('groups.json', groups)
		
	elif msg.text.startswith(config['command_start'] + 'list'):
		if input == 'groups':
			message = '*Groups:*'
			for group in groups.items():
				if group[1]['hide'] != True:
					message += '\n\t' + group[1]['title'] + ' \[' + group[1]['realm'] + '] (' + group[0] + ')'
		elif input == 'mods':
			message = '*Mods for ' + groups[str(msg.chat.id)]['title'] + ':*'
			for mod in groups[str(msg.chat.id)]['mods'].items():
				message += '\n\t' + mod[1]
	
	elif msg.text.startswith(config['command_start'] + 'info'):
		if str(msg.chat.id) in groups:
			message = '*Info of ' + groups[str(msg.chat.id)]['title'] + ' [' + groups[str(msg.chat.id)]['realm'] + ']*'
			message += '\n_' + groups[str(msg.chat.id)]['description'] + '_'
			if groups[str(msg.chat.id)]['rules'] != '':
				message += '\n\n*Rules:*\n' + groups[str(msg.chat.id)]['rules']
			if groups[str(msg.chat.id)]['locale'] != 'default':
				message += '\n\n*Locale:* _' + groups[str(msg.chat.id)]['locale'] + '_'
			if groups[str(msg.chat.id)]['link'] != '':
				message += '\n\n*Invite link:*\n' + groups[str(msg.chat.id)]['link']
		else:
			message = 'Group not added.'
	
	elif msg.text.startswith(config['command_start'] + 'broadcast'):
		message = 'Unsupported action.'
		
	elif msg.text.startswith(config['command_start'] + 'kick'):
		message = 'Unsupported action.'
		
	elif msg.text.startswith(config['command_start'] + 'rules'):
		message = 'Unsupported action.'
		
	elif msg.text.startswith(config['command_start'] + 'promote'):
		groups[str(msg.chat.id)]['mods'][str(msg.from_user.id)] = str(msg.from_user.first_name)
		message = msg.from_user.first_name + ' is now a moderator.'
		save_json('groups.json', groups)
		
	elif msg.text.startswith(config['command_start'] + 'demote'):
		del groups[str(msg.chat.id)]['mods'][str(msg.from_user.id)]
		message = msg.from_user.first_name + ' is not a moderator.'
		save_json('groups.json', groups)
		
	elif msg.text.startswith(config['command_start'] + 'join'):
		if (input in groups):
			if groups[input]['link'] != '':
				message = groups[input]['link']
			else:
				message = 'No invite link available.'
		else:
			message = 'Group not found.'
		
	core.send_message(msg.chat.id, message, parse_mode="Markdown")