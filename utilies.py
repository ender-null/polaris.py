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

def on_msg_receive(msg):
	
 	msg = process_msg(msg)
	
 	if msg.date < time.mktime(datetime.datetime.now().timetuple()) - 10:
 		return
 	if not hasattr(msg, 'text'):
 		return

 	lower = msg.text.lower()

	for i,v in plugins.items():
		for t in v.triggers:
			if re.compile(t).search(lower):
				if hasattr(v, 'typing'):
					core.send_chat_action(msg.chat.id, 'typing')
				if config.debug == False:
					try:	
						v.action(msg)
					except Exception as e:
						core.send_message(msg.chat.id, str(e))
				else:
					v.action(msg)
					
def bot_init():
	print('Fetching bot information...')
	global core
	core = telebot.TeleBot(config.apis['telegram_bot'])
	
	global bot
	bot = core.get_me()
	while bot == False:
		print('\033[91mFailure fetching bot information. Trying again...\033[0m')
		bot = core.get_me()

	print('Loading plugins...')
	global plugins
	plugins = {}
	plugins = load_plugins()

	print('Plugins loaded: ' + str(len(plugins)) + '.')
	
	print('@' + str(bot.username) + ', AKA ' + str(bot.first_name) + ' (' + str(bot.id) + ')')

	global is_started
 	is_started = True
 	
def process_msg(msg):
	if hasattr(msg, 'new_chat_participant'):
		if msg.new_chat_participant.id != bot.id:
			msg.text = 'hi ' + str(bot.first_name)
			msg.from_user = msg.new_chat_participant
		else:
			msg.text = '/about'

	if hasattr(msg, 'left_chat_participant'):
		if msg.left_chat_participant.id != bot.id:
			msg.text = 'bye ' + str(bot.first_name)
			msg.from_user = msg.left_chat_participant
	return msg

def load_plugins():
	for p in config.plugins:
		try:
			print('\033[92m\tLoading plugin: ' + p + '\033[0m')
			plugins[p] = importlib.import_module('plugins.{}'.format(p))
		except Exception as e:
			print('\033[91m\tError loading plugin ' + p + '\033[0m')
			print('\033[91m\t' + str(e) + '\033[0m')
	
	return plugins

def get_input(text):
	if not ' ' in text:
		return False
	return text[text.find(" ") + 1:]

def first_word(text):
	if not ' ' in text:
		return False
	return text.split(' ', 1)[0]
	
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
	'''
	if os.path.splitext(filename)[1][1:]=='mp3':
		print '\t\tmp3 found!'
		filename = convert_to_voice(tmp, filename)
		print '\t\tConverted to: ' + filename
	'''
	file = open(tmp + filename, 'rb')
	
	if type == 'photo':
		core.send_chat_action(chat, 'upload_photo')
		if extension == 'gif':
			core.send_document(chat, file)
		else:
			core.send_photo(chat, file, caption)
	elif type == 'audio':
		core.send_chat_action(chat, 'upload_audio')
		core.send_document(chat, file)
	elif type == 'voice':
		core.send_chat_action(chat, 'upload_voice')
		core.send_document(chat, file)
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
	output_name = os.path.splitext(file_name)[0] + '.opus'
	cmd = 'avconv -i ' + path + file_name + ' -f wav - | opusenc --downmix-mono - ' + path + output_name
	
	print cmd
	
	subprocess.call(cmd)
	os.remove(path + file_name)
	return output_name
	
def tag_replace(text, msg):
	tags = {
		'#FROM_FIRSTNAME': msg.from_user.first_name,
		'#FROM_USERNAME': msg.from_user.username,
		'#BOT_FIRSTNAME': bot.first_name,
		'#BOT_USERNAME': bot.username,
		'#BOT_NAME': bot.first_name.split('-')[0],
		'	': '',
	}
	
	for k,v in tags.items():
		if k in text:
			text = text.replace(k, v)
	return text