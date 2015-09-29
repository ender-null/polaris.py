import __main__
import config
import os
import utilies
import requests
import urllib
import json
import random
import re

doc = '	/cat\nGet a cat pic!'
triggers = {
	'^/cats?'
}

def action(msg):			

	url = 'http://thecatapi.com/api/images/get'
	params = {
		'format': 'src',
		'api_key': config.apis['catapi'],
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return __main__.tb.send_message(msg.chat.id, config.locale.errors['connection'] + '\nError: ' + str(jstr.status_code))
	
	result_url = jstr.url
	
	utilies.download_and_send(__main__.tb, msg.chat.id, url, 'photo', params=params)

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
}