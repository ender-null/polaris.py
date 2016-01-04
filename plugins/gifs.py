# -*- coding: utf-8 -*-
from utils import *
import random

commands = [
    '^gif',
    '^giphy',
    '^gifnsfw'
]

parameters = {('query', True)}

description = 'This command performs a Google Images search for the given query. One random top result is returned. Safe search is enabled by default; use *' + config['command_start'] + 'insfw* to get potentially NSFW results.'
description = 'Returns a random or search-resulted GIF from giphy.com. Results are limited to PG-13 by default; use *' + config['command_start'] + 'gifnsfw* to get potentially NSFW results.'
action = 'upload_photo'

def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://api.giphy.com/v1/gifs/search?limit=10&api_key='
    params = {
        'api_key': config['api']['giphy'],
        'limit': 32,
        'rating': 'pg-13',
        'q': input
    }

    if get_command(msg['text']) == 'gifnsfw':
        params['rating'] = 'r'

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        return send_error(msg, 'connection')

    jdat = json.loads(jstr.text)

    if len(jdat['data']) == 0:
        return send_error(msg, 'results')
        
    i = random.randint(1, len(jdat['data']))-1
    result_url = jdat['data'][i]['images']['original']['url']
    
    photo = download(result_url)

    if photo:
        send_document(msg['chat']['id'], photo)
    else:
        send_error(msg, 'download')


def inline(qry):
    input = get_input(qry['query'])

    url = 'http://api.giphy.com/v1/gifs/search?limit=10&api_key='
    params = {
        'api_key': config['api']['giphy'],
        'limit': 16,
        'rating': 'pg-13',
        'q': input
    }

    if first_word(qry['query']) == 'gifnsfw':
        params['rating'] = 'r'

    jstr = requests.get(url, params=params)
    jdat = json.loads(jstr.text)

    results_json = []
    for item in jdat['data']:
        result = {
            'type': 'gif',
            'id': item['id'],
            'gif_url': item['images']['original']['url'],
            'gif_width': int(item['images']['original']['width']),
            'gif_height': int(item['images']['original']['height']),
            'thumb_url': item['images']['fixed_width_small']['url'],
            'thumb_width': int(item['images']['fixed_width_small']['width']),
            'thumb_height': int(item['images']['fixed_width_small']['height'])
        }
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(qry['id'], results)
