from core.utils import *
import random

commands = [
    ('/gif', ['query']),
    ('/gifnsfw', ['query'])
]
description = 'Returns a random or search-resulted GIF from giphy.com. Results are limited to PG-13 by default.'


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    url = 'http://api.giphy.com/v1/gifs/search?limit=10&api_key='
    params = {
        'api_key': config.keys.giphy,
        'limit': 32,
        'rating': 'pg-13',
        'q': input
    }

    if get_command(m) == 'gifnsfw':
        params['rating'] = 'r'

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        send_alert(m, '%s\n%s' % (lang.errors.connection, jstr.text))
        return send_message(m, lang.errors.connection)

    jdat = json.loads(jstr.text)

    if len(jdat['data']) == 0:
        return send_message(m, lang.errors.results)

    i = random.randint(1, len(jdat['data'])) - 1
    result_url = jdat['data'][i]['images']['original']['url']
    caption = '"{0}"  {1}'.format(input, get_short_url(result_url).lstrip('https://'))
    
    photo = download(result_url)

    if photo:
        send_document(m, photo, caption)
    else:
        send_message(m, lang.errors.download)

def inline(m):
    input = get_input(m)

    url = 'http://api.giphy.com/v1/gifs/search?limit=10&api_key='
    params = {
        'api_key': config.keys.giphy,
        'limit': 16,
        'rating': 'pg-13',
        'q': input
    }

    if get_command(m) == 'gifnsfw':
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
    answer_inline_query(m, results)