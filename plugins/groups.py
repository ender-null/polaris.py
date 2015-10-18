from __main__ import *
from utilies import *

triggers = {
	'^' + config['command_start'] + 'add',
	'^' + config['command_start'] + 'remove',
	'^' + config['command_start'] + 'list',
	'^' + config['command_start'] + 'info',
	'^' + config['command_start'] + 'modcast',
	'^' + config['command_start'] + 'modkick',
	'^' + config['command_start'] + 'join',
}

def action(msg):			
	input = get_input(msg.text)
	
	message = locale['default']['errors']['argument']
	
	if msg.from_user.id not in config['admin']:
		return core.send_message(msg.chat.id, locale['default']['errors']['permission'])
	
	if msg.text.startswith(config['command_start'] + 'add'):
		if not str(msg.chat.id) in groups:
			groups[str(msg.chat.id)] = {}
			groups[str(msg.chat.id)]['link'] = ''
			groups[str(msg.chat.id)]['realm'] = ''
			groups[str(msg.chat.id)]['title'] = msg.chat.title
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
		
	elif msg.text.startswith(config['command_start'] + 'remove'):
		del groups[str(msg.chat.id)]
		message = 'Group removed'
		
	elif msg.text.startswith(config['command_start'] + 'list'):
		if input == 'groups':
			message = '*Groups:*'
			for group in groups.items():
				if group[1]['hide'] != True:
					message += '\n\t' + group[1]['title'] + ' (' + group[0] + ')'
		elif input == 'mods':
			message = '*Mods for ' + groups[str(msg.chat.id)]['title'] + ':*'
			for mod in groups[str(msg.chat.id)]['mods'].items():
				message += '\n\t' + mod[1]
	
	elif msg.text.startswith(config['command_start'] + 'info'):
		if str(msg.chat.id) in groups:
			message = '*Info of ' + groups[str(msg.chat.id)]['title'] + '*'
			message += '\n_' + groups[str(msg.chat.id)]['description'] + '_'
			message += '\n\n*Rules:*\n' + groups[str(msg.chat.id)]['rules']
			message += '\n\n*Invite link:*\n' + groups[str(msg.chat.id)]['link']
		else:
			message = 'Group not added.'
	
	elif msg.text.startswith(config['command_start'] + 'modcast'):
		message = 'Unsupported action.'
		
	elif msg.text.startswith(config['command_start'] + 'modkick'):
		message = 'Unsupported action.'
		
	elif msg.text.startswith(config['command_start'] + 'join'):
		if (input in groups):
			message = groups[input]['link']
		else:
			message = 'Group not found.'
		
	core.send_message(msg.chat.id, message, parse_mode="Markdown")