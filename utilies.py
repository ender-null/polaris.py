import os
import config
import time
import datetime
import requests
import subprocess
import magic
import importlib

def load_plugins():
	plugins = {}
	for p in config.plugins:
		try:
			p = p[:-3] if p.endswith('.py') else p
			print("\tLoading plugin: {}".format(p))
			if plugins.get(p):
				m = importlib.reload(plugins[p])
			else:
				m = importlib.import_module('plugins.{}'.format(p))
			plugins[p] = m
		except Exception as e:
			print('\033[31m\tError loading plugin {}\033[39m'.format(p))
			print('\033[31m\t{}\033[39m'.format(e))
	
	return plugins

def get_input(text):
	if not ' ' in text:
		return False
	return text[text.find(" ") + 1:]
	
def download_and_send(bot, chat, url, type=None, caption=None, headers=None, params=None):
	
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
		return bot.send_message(chat, config.locale.errors['download'])
		
	filename = fix_extension(tmp, filename)
	'''
	if os.path.splitext(filename)[1][1:]=='mp3':
		print '\t\tmp3 found!'
		filename = convert_to_voice(tmp, filename)
		print '\t\tConverted to: ' + filename
	'''
	file = open(tmp + filename, 'rb')
	
	if type == 'photo':
		bot.send_chat_action(chat, 'upload_photo')
		if extension == 'gif':
			bot.send_document(chat, file)
		else:
			bot.send_photo(chat, file, caption)
	elif type == 'audio':
		bot.send_chat_action(chat, 'upload_audio')
		bot.send_document(chat, file)
	elif type == 'voice':
		bot.send_chat_action(chat, 'upload_voice')
		bot.send_document(chat, file)
	elif type == 'sticker':
		bot.send_document(chat, file)
	else:
		bot.send_chat_action(chat, 'upload_document')
		bot.send_document(chat, file)
		
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
	if mimetype == 'audio/mpeg':
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