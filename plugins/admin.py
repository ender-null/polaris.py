import __main__
import config
import os
import utilies
import requests
import urllib
import json
import random
import re

triggers = {
	'^/run ',
	'^/reload',
	'^/msg ',
	'^/stop',
}

def action(msg):			
	input = utilies.get_input(msg.text)
	message = config.locale.errors['argument']
	
	if msg.from_user.id not in config.admins:
		return __main__.tb.send_message(msg.chat.id, config.locale.errors['permission'])
	
	if msg.text.startswith('/run'):
		print 'run'
	elif msg.text.startswith('/reload'):
		print 'reload'
		
		reload(config)
		reload(utilies)
		__main__.bot_init()
		__main__.plugins = utilies.load_plugins()
		
		message = 'Bot reloaded!'
	elif msg.text.startswith('/msg'):
		print 'msg'
	elif msg.text.startswith('/stop'):
		print 'stop'
		__main__.is_started = False
		message = 'Shutting down...'
		
	__main__.tb.send_message(msg.chat.id, message)

plugin = {
    'triggers': triggers,
    'action': action,
    'typing': None,
}