# -*- coding: utf-8 -*-
from utils import *
import random
from requests.auth import HTTPBasicAuth

commands = [
    '^image',
    '^img',
    '^i ',
    '^insfw'
]

parameters = {('query', True)}

description = 'This command performs a Google Images search for the given query. One random top result is returned. Safe search is enabled by default; use *' + config['command_start'] + 'insfw* to get potentially NSFW results.'
action = 'upload_photo'

exts = {
    '.jpg$',
    '.jpeg$',
    '.gif$',
    '.png$',
    '.tif$',
    '.bmp$'
}


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Image'
    params = {
        'Query': "'" + input + "'",
        'Adult': "'Moderate'",
        '$format': 'json',
        '$top': '8'
    }
    auth = HTTPBasicAuth(config['api']['azurekey'], config['api']['azurekey'])

    if get_command(msg['text']) == 'insfw':
        params['Adult'] = "'Off'"

    jstr = requests.get(url, params=params, auth=auth)

    if jstr.status_code != 200:
        return send_error(msg, 'connection', jstr.status_code)

    jdat = json.loads(jstr.text)

    if not len(jdat['d']['results']) != 0:
        return send_error(msg, 'results')

    is_real = False
    counter = 0
    while not is_real:
        counter = counter + 1
        if counter > 5 or jdat['d']['results'] == '0':
            return send_error(msg, 'results')

        i = random.randint(1, len(jdat['d']['results']))-1

        result_url = jdat['d']['results'][i]['MediaUrl']
        caption = u'"{0}"  {1}'.format(input, get_short_url(result_url).lstrip('https://'))

        for v in exts:
            if re.compile(v).search(result_url):
                is_real = True

    photo = download(result_url)

    if photo:
        send_photo(msg['chat']['id'], photo, caption=caption)
    else:
        send_error(msg, 'download')

def inline(qry):
    input = get_input(qry['query'])

    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Image'
    params = {
        'Query': "'" + str(input) + "'",
        'Adult': "'Moderate'",
        '$format': 'json',
        '$top': '8'
    }
    auth = HTTPBasicAuth(config['api']['azurekey'], config['api']['azurekey'])

    if first_word(input) == 'insfw':
        params['Adult'] = "'Off'"

    jstr = requests.get(url, params=params, auth=auth)
    jdat = json.loads(jstr.text)

    results_json = []
    for item in jdat['d']['results']:
        result = {
            'type': 'photo',
            'id': item['ID'],
            'photo_url': item['MediaUrl'],
            'photo_width': int(item['Width']),
            'photo_height': int(item['Height']),
            'thumb_url': item['Thumbnail']['MediaUrl']
        }
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(qry['id'], results)

