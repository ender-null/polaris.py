# -*- coding: utf-8 -*-
from __main__ import *
import config
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
import platform

def bot_init():
	reload(config)
	print('Getting bot data...')
	global core
	core = telebot.TeleBot(config.api['telegram_bot'])
	
	global bot
	bot = core.get_me()
	while bot == False:
		print('\tFailure getting bot data. Trying again...')
		bot = core.get_me()
	print('\tFirst name:\t' + bot.first_name)
	print('\tUsername:\t' + bot.username)
	print('\tUser id:\t' + str(bot.id))

	print('\nLoading plugins...')
	global plugins
	plugins = {}
	plugins = load_plugins()

	global is_started
 	is_started = True
	print('\n' + bot.first_name + ' is started!')
	
def on_message_receive(msg):
	
 	msg = process_message(msg)
	
	if config.ignore['old_messages']==True and msg.date < time.mktime(datetime.datetime.now().timetuple()) - 10:
		return
 	if config.ignore['media']==True and not hasattr(msg, 'text'):
 		return
	
	if not hasattr(msg, 'text'):
		msg.text = ''
	lower = msg.text.lower()

	for i,v in plugins.items():
		for t in v.triggers:
			t = tag_replace(t, msg)
			if re.compile(t).search(lower):
				if hasattr(v, 'typing'):
					core.send_chat_action(msg.chat.id, 'typing')
					
				if config.handle_exceptions == True:
					try:	
						v.action(msg)
					except Exception as e:
						core.send_message(config.admin_group, str(e))
				else:
					v.action(msg)
					 	
def process_message(msg):
	if (config.process['new_chat_participant']==True
	and hasattr(msg, 'new_chat_participant')):
		if msg.new_chat_participant.id != bot.id:
			msg.text = 'hi ' + str(bot.first_name)
			msg.from_user = msg.new_chat_participant
		else:
			msg.text = '/about'
	
	if (config.process['left_chat_participant']==True
	and hasattr(msg, 'left_chat_participant')):
		if msg.left_chat_participant.id != bot.id:
			msg.text = 'bye ' + str(bot.first_name)
			msg.from_user = msg.left_chat_participant
	
	if (config.process['reply_to_message']==True
	and hasattr(msg, 'reply_to_message')
	and hasattr(msg.reply_to_message, 'text')
	and hasattr(msg, 'text')
	and msg.chat.id != config.admin_group):
		if msg.reply_to_message.from_user.id == bot.id and not msg.text.startswith(config.command_start):
			msg.text = str(bot.first_name) + ' ' + msg.text
		elif msg.text.startswith(config.command_start):
			msg.text += ' ' + msg.reply_to_message.text
	
	if (config.process['chatter']==True
	and hasattr(msg, 'text')
	and msg.chat.type == 'private'
	and not msg.text.startswith(config.command_start)
	and msg.chat.id != config.admin_group):
		msg.text = str(bot.first_name) + ' ' + msg.text
		
	return msg

def load_plugins():
	for plugin in config.plugins:
		try:
			plugins[plugin] = importlib.import_module('plugins.' + plugin)
			print('\t[OK] ' + plugin)
		except Exception as e:
			print('\t[Failed] ' + plugin + ': ' + str(e))
	
	print('\n\tLoaded: ' + str(len(plugins)) + '/' + str(len(config.plugins)))
	return plugins
	
def load_plugins_new():
	plugins_loaded = {}
	for plugin in config.plugins:
		try:
			plugins_loaded[plugin] = importlib.import_module('plugins.' + plugin)
			print('\t[OK] ' + plugin)
		except Exception as e:
			print('\t[Failed] ' + plugin + ': ' + str(e))
	
	print('\n\tLoaded: ' + str(len(plugins_loaded)) + '/' + str(len(config.plugins)))
	return plugins_loaded

def get_input(text):
	if not ' ' in text:
		return False
	return text[text.find(" ") + 1:]

def first_word(text):
	if not ' ' in text:
		return False
	return text.split()[0]

def last_word(text):
	if not ' ' in text:
		return False
	return text.split()[-1] 
	
def download_and_send(chat, url, type=None, caption=None, headers=None, params=None):	
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
		return core.send_message(chat, config.locale.errors['download'], parse_mode="Markdown")
		
	filename = fix_extension(tmp, filename)
	
	if type=='voice':
		filename = convert_to_voice(tmp, filename)
	
	file = open(tmp + filename, 'rb')
	
	if type == 'photo':
		core.send_chat_action(chat, 'upload_photo')
		if extension == 'gif':
			core.send_document(chat, file)
		else:
			core.send_photo(chat, file, caption)
	elif type == 'audio':
		core.send_chat_action(chat, 'upload_audio')
		core.send_audio(chat, file)
	elif type == 'voice':
		core.send_chat_action(chat, 'upload_voice')
		core.send_voice(chat, file)
	elif type == 'sticker':
		core.send_document(chat, file)
	else:
		core.send_chat_action(chat, 'upload_document')
		core.send_document(chat, file)
		
	clean_temporal(tmp, filename)

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
	else:
		return None
		
def convert_to_voice(path, file_name):
	output_name = os.path.splitext(file_name)[0] + '.ogg'
	
	cmd = 'avconv -i ' + path + file_name + ' -f wav - | opusenc --downmix-mono - ' + path + output_name
	subprocess.call(cmd, shell=True, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
	
	os.remove(path + file_name)
	
	return output_name
	
def tag_replace(text, msg):
	dt = datetime.datetime.now()
	greeting = 'Hi'

	if dt.hour >= 5 and dt.hour < 12 :
		greeting = config.locale.greeting['morning']
	elif dt.hour <= 12 and dt.hour < 17:
		greeting = config.locale.greeting['afternoon']
	elif dt.hour <= 17 and dt.hour < 21:
		greeting = config.locale.greeting['evening']
	else:
		greeting = config.locale.greeting['night']
	
	goodbye = 'Goodbye'
	if dt.hour >= 5 and dt.hour < 12 :
		goodbye = config.locale.goodbye['morning']
	elif dt.hour <= 12 and dt.hour < 17:
		goodbye = config.locale.goodbye['afternoon']
	elif dt.hour <= 17 and dt.hour < 21:
		goodbye = config.locale.goodbye['evening']
	else:
		goodbye = config.locale.goodbye['night']

	tags = {
		'#FROM_FIRSTNAME': escape_markup(msg.from_user.first_name),
		'#BOT_FIRSTNAME': escape_markup(bot.first_name),
		'#BOT_USERNAME': escape_markup(bot.username),
		'#GREETING': greeting,
		'#GOODBYE': goodbye,
		'#BOT_NAME': escape_markup(bot.first_name.split('-')[0]),
		'#BOT_NAME_LOWER': escape_markup(bot.first_name.split('-')[0].lower()),
		'#SMILE': u'😄',
		'#SAD': u'😔',
		'#EMBARASSED': u'😳',
		'	': '',
	}
	
	if msg.from_user.username:
		tags['#FROM_USERNAME'] = escape_markup(msg.from_user.username)
	
	for k,v in tags.items():
		if k in text:
			text = text.replace(k, v)
	return text

def escape_markup(text):
	text = text.replace("_", "\_")
	text = text.replace("*", "\*")
	text = text.replace("`", "\`")
	text = text.replace("```", "\```")
	return text