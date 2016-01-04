# -*- coding: utf-8 -*-
from utils import *
import random


commands = [
    '^konachan',
    '^kc ',
    '^k ',
    '^knsfw',
]

parameters = {('tags', True)}

description = 'Gets an image from [Konachan](http://konachan.com), use *' + config['command_start'] + 'knsfw* to get potentially NSFW results.'
action = 'upload_photo'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    tags = input
    if not get_command(msg['text']) == 'knsfw':
        tags += ' rating:s'

    url = 'http://konachan.com/post.json'
    params = {
        'limit': 100,
        'tags': tags
    }

    jdat = send_request(
        url,
        params=params
    )

    if len(jdat) < 1:
        return send_error(msg, 'results')

    i = random.randint(1, len(jdat))-1

    if not jdat:
        return send_error(msg, 'connection', jstr.status_code)

    result_url = jdat[i]['file_url']
    caption = str(len(jdat)) + ' results matching: "' + input + '"'

    photo = download(result_url)

    if photo:
        send_photo(msg['chat']['id'], photo, caption=caption)
    else:
        send_error(msg, 'download')


def inline(qry):
    input = get_input(qry['query'])

    tags = input
    if not first_word(qry['query']) == 'knsfw':
        tags += ' rating:s'

    url = 'http://konachan.com/post.json'
    params = {
        'limit': 16,
        'tags': tags
    }

    jstr = requests.get(url, params=params)
    jdat = json.loads(jstr.text)

    results_json = []
    for item in jdat:
        result = {
            'type': 'photo',
            'id': str(item['id']),
            'photo_url': item['file_url'],
            'photo_width': int(item['width']),
            'photo_height': int(item['height']),
            'thumb_url': item['preview_url'],
        }
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(qry['id'], results)
