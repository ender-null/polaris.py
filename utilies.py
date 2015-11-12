# -*- coding: utf-8 -*-

from __main__ import *
from bindings import *

import telebot
import os
import time
import datetime
import requests
import subprocess
import magic
import importlib
import urllib
import json
import random
import re
import sys
import json
import platform
from collections import OrderedDict

def bot_init():
	print('Loading config... ')
	global config
	config = load_json('data/config.json')
	
	global groups
	groups = load_json('data/groups.json')
	
	global locale
	locale = OrderedDict()
	for file in config['locales']:
		locale[file] = load_json('locale/' + file + '.json')
	
	print('\nGetting bot data...')
	global bot
	bot = get_me()
	while bot == False:
		print('\tFailure getting bot data. Trying again...')
		bot = get_me()
	bot = bot['result']
	print('\tFirst name:\t' + bot['first_name'])
	print('\tUsername:\t' + bot['username'])
	print('\tUser id:\t' + str(bot['id']))

	print('\nLoading plugins...')
	global plugins
	plugins = OrderedDict()
	plugins = load_plugins()

	global is_started
 	is_started = True
	print('\n' + bot['first_name'] + ' is started!')
	
def on_message_receive(msg):
 	msg = process_message(msg)
	now = time.mktime(datetime.datetime.now().timetuple())
	
	if config['ignore']['old_messages']==True and msg['date'] < now - 10:
		return
 	if config['ignore']['media']==True and not msg['text']:
 		return
	
	if not msg['text']:
		msg['text'] = ''
	lower = msg['text'].lower()
	
	for i,plugin in plugins.items():
		for command in plugin.commands:
			trigger = command.replace("^", "^" + config['command_start'])
			trigger = tag_replace(trigger, msg)
			if re.match(trigger, lower):
				if config['handle_exceptions'] == True:
					try:
						if hasattr(plugin, 'action'):
							send_chat_action(msg['chat']['id'], plugin.action)
						plugin.run(msg)
					except Exception as e:
						#send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['exception'])
						for group in groups.items():
							if group[1]['special'] == 'alerts':
								send_message(group[0], str(e))
				else:
					plugin.run(msg)
					 	
def process_message(msg):
	if (config['process']['new_chat_participant']==True
	and hasattr(msg, 'new_chat_participant')):
		if msg['new_chat_participant']['id'] != bot['id']:
			msg['text'] = '!new_chat_participant'
			msg['from'] = msg['new_chat_participant']
		else:
			msg['text'] = '/about'
	
	if (config['process']['left_chat_participant']==True
	and hasattr(msg, 'left_chat_participant')):
		if msg['left_chat_participant']['id'] != bot['id']:
			msg['text'] = '!left_chat_participant'
			msg['from'] = msg['left_chat_participant']
	
	if (config['process']['reply_to_message']==True
	and hasattr(msg, 'reply_to_message')
	and hasattr(msg['reply_to_message'], 'text')
	and hasattr(msg, 'text')):
		if str(msg['chat']['id']) in groups and groups[str(msg['chat']['id'])]['special'] != 'log':
			if msg['reply_to_message']['from']['id'] == bot['id'] and not msg['text'].startswith(config['command_start']):
				msg['text'] = bot['first_name'] + ' ' + msg['text']
			elif msg['text'].startswith(config['command_start']):
				msg['text'] += ' ' + msg['reply_to_message']['text']
	
	if (config['process']['chatter']==True
	and hasattr(msg, 'text')
	and msg['chat']['type'] == 'private'
	and not msg['text'].startswith(config['command_start'])):
		msg['text'] = bot['first_name'] + ' ' + msg['text']

	return msg

def load_plugins():
	for plugin in config['plugins']:
		try:
			plugins[plugin] = importlib.import_module('plugins.' + plugin)
			print('\t[OK] ' + plugin)
		except Exception as e:
			print('\t[Failed] ' + plugin + ': ' + str(e))
	
	print('\n\tLoaded: ' + str(len(plugins)) + '/' + str(len(config['plugins'])))
	return plugins
	
def save_json(path, data):
	try:
		with open(path, 'w') as f:
			print('\t[OK] ' + path)
			json.dump(data, f, sort_keys=True, indent=4)
	except:
		print(colored.red('\t[Failed] ' + path))
		pass


def load_json(path):
	try:
		with open(path, 'r') as f:
			print('\t[OK] ' + path)
			return json.load(f)
	except:
		print('\t[Failed] ' + path)
		return {}

def get_command(text):
	if text.startswith(config['command_start']):
		return text.split(' ')[0].lstrip(config['command_start'])

def get_input(text):
	if not ' ' in text:
		return False
	return text[text.find(" ") + 1:]

def first_word(text, i=0):
	if not ' ' in text:
		return False
	return text.split()[i-1]

def all_but_first_word(text):
	if not ' ' in text:
		return False
	return text.replace(first_word(text) + ' ', '')
	
def last_word(text):
	if not ' ' in text:
		return False
	return text.split()[-1]
		
def get_coords(input):
	url = 'http://maps.googleapis.com/maps/api/geocode/json'
	params = {
		'address': input
	}
		
	jdat = send_request(url, params = params,)
	
	if jdat['status'] == 'ZERO_RESULTS':
		return False,False,False,False
	
	locality = jdat['results'][0]['address_components'][0]['long_name']
	for address in jdat['results'][0]['address_components']:
		if 'country' in address['types']:
			country = address['long_name']

	return jdat['results'][0]['geometry']['location']['lat'], jdat['results'][0]['geometry']['location']['lng'], locality, country
	
def get_locale(chat_id):
	if str(chat_id) in groups:
		return groups[str(chat_id)]['locale']
	else:
		return 'default'

def download(url, headers=None, params=None):	
	name = os.path.splitext(str(time.mktime(datetime.datetime.now().timetuple())))[0]
	extension = os.path.splitext(url)[1][1:]
	if extension == '':
		filename = name
	else:
		filename = name + '.' + extension

	tmp = 'tmp/'
	open_temporal(tmp)
	
	try:
		jstr = requests.get(url, params=params, headers=headers, stream=True)
		with open(tmp + filename, 'wb') as f:
			for chunk in jstr.iter_content(chunk_size=1024): 
				if chunk:
					f.write(chunk)
					f.flush()
	except IOError, e:
		return None
		
	filename = fix_extension(tmp, filename)
		
	file = open(tmp + filename, 'rb')	
	clean_temporal(tmp, filename)
	return file

def open_temporal(tmp):
	if not os.path.exists(tmp):
		os.makedirs(tmp)
	
def clean_temporal(tmp, filename):
	if os.path.exists(tmp):
		if os.path.isfile(tmp + filename):
			os.remove(tmp + filename)
		
		try:
			os.rmdir(tmp)
		except OSError:
			print('Temporal folder (' + tmp + ') is not empty.')
			
def fix_extension(file_path, file_name):
	extension = os.path.splitext(file_path + file_name)[1][1:]
	if extension == '':
		mime = magic.Magic(mime=True)
		mimetype = mime.from_file(file_path + file_name)
		extension = '.' + mime_match(mimetype)
		
		if extension != None:
			os.rename(file_path + file_name, file_path + file_name + extension)
			return file_name + extension
		else:
			return file_name
	else:
		return file_name
			
def mime_match(mimetype):
	if mimetype == 'image/png':
		return 'png'
	elif mimetype == 'image/jpeg':
		return 'jpg'
	elif mimetype == 'image/gif':
		return 'gif'
	elif mimetype == 'audio/mpeg':
		return 'mp3'
	elif mimetype == 'text/plain':
		return 'txt'
	else:
		return None
	
def tag_replace(text, msg):
	dt = datetime.datetime.now()

	if dt.hour >= 5 and dt.hour < 12 :
		greeting = locale[get_locale(msg['chat']['id'])]['greeting']['morning']
	elif dt.hour <= 12 and dt.hour < 17:
		greeting = locale[get_locale(msg['chat']['id'])]['greeting']['afternoon']
	elif dt.hour <= 17 and dt.hour < 21:
		greeting = locale[get_locale(msg['chat']['id'])]['greeting']['evening']
	else:
		greeting = locale[get_locale(msg['chat']['id'])]['greeting']['night']
	
	if dt.hour >= 5 and dt.hour < 12 :
		goodbye = locale[get_locale(msg['chat']['id'])]['goodbye']['morning']
	elif dt.hour <= 12 and dt.hour < 17:
		goodbye = locale[get_locale(msg['chat']['id'])]['goodbye']['afternoon']
	elif dt.hour <= 17 and dt.hour < 21:
		goodbye = locale[get_locale(msg['chat']['id'])]['goodbye']['evening']
	else:
		goodbye = locale[get_locale(msg['chat']['id'])]['goodbye']['night']

	tags = {
		'#FROM_FIRSTNAME': escape_markup(msg['from']['first_name']),
		'#BOT_FIRSTNAME': escape_markup(bot['first_name']),
		'#BOT_USERNAME': escape_markup(bot['username']),
		'#GREETING': greeting,
		'#GOODBYE': goodbye,
		'#BOT_NAME_LOWER': escape_markup(bot['first_name'].split('-')[0].lower()),
		'#BOT_NAME': escape_markup(bot['first_name'].split('-')[0]),
		'	': '',
	}
	
	if hasattr(msg['from'], 'username'):
		tags['#FROM_USERNAME'] = escape_markup(msg['from']['username'])
	else:
		tags['#FROM_USERNAME'] = None
	
	for k,v in tags.items():
		if k in text:
			text = text.replace(k, v)
	return text

def escape_markup(text):
	characters = ['_', '*', '[', ')', '`']
	
	for character in characters:
		text = text.replace(character, '\\' + character)

	return text

def delete_markup(text):
	characters = ['_', '*', '[', ']', '(', ')', '`']
	
	for character in characters:
		text = text.replace(character, '')

	return text

def get_doc(commands, parameters, description):
	doc = commands[0].replace('^', config['command_start'])
	if parameters:
		doc += format_parameters(parameters)
	doc += '\n' + description
	return doc

def format_parameters(parameters):
	formated_parameters = ''
	for parameter,required in parameters:
		if required == True:
			formated_parameters += ' *<' + parameter + '>*'
		else:
			formated_parameters += ' \[' + parameter + ']'
	return formated_parameters
	
def is_admin(msg):
	if msg['from']['id'] in config['admin']:
		return True
	else:
		return False
		
def is_mod(msg):
	if (is_admin(msg)
	or str(msg['from']['id']) in groups[str(msg['chat']['id'])]['mods']):
		return True
	else:
		return False
		
def get_size(number):
	size = ''
	unit = 0
	
	units = [
		'',
		'K',
		'M',
		'G',
		'T'
	]
	
	while (number > 1024):
		number = number/1024
		unit = unit + 1
		
	return str(number),units[unit]
	
def send_error(msg, error_type, error_id=200):
	loc = get_locale(msg['chat']['id'])
	message = locale[loc]['errors'][error_type].format(error_id)
	send_message(msg['chat']['id'], message)