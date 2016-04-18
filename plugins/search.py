from core.utils import *
from bs4 import BeautifulSoup

commands = [
    ('/search', ['query']),
    ('/snsfw', ['query'])
]
description = 'This command performs a Google search for the given query.'
shortcut = ['/s ', None]


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    url = 'https://ajax.googleapis.com/ajax/services/search/web'
    params = {
        'v': 1.0,
        'q': input,
        'safe': 'active',
        'rsz': '8'
    }

    if get_command(m) == 'insfw':
        del params['safe']

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        send_alert('%s\n%s' % (lang.errors.connection, jstr.text))
        return send_message(m, lang.errors.connection, markup='HTML')

    jdat = json.loads(jstr.text)

    print(len(jdat['responseData']['results']))

    if not len(jdat['responseData']['results']) != 0:
        return send_message(m, lang.errors.results, markup='HTML')

    output = '<b>Google search for:</b> <i>%s</i>\n' % input
    for result in jdat['responseData']['results']:
        title = result['titleNoFormatting']
        url = result['unescapedUrl']
        output += '\t🌐\t<a href="%s">%s</a>\n' % (url, title)
    
    send_message(m, output, markup='HTML')


def inline(m):
    input = get_input(m)
    query = ''
    caption = ''
    if input and '|' in input and input[-1] != '|':
        query, caption = input.split('|')
    else:
        query = input

    url = 'https://ajax.googleapis.com/ajax/services/search/web'
    params = {
        'v': 1.0,
        'q': input,
        'rsz': '8'
    }

    if get_command(m) == 'insfw':
        del params['safe']

    jstr = requests.get(url, params=params)
    
    results_json = []
    
    if jstr.status_code != 200:
        message = {
            'message_text': '%s\n%s' % (lang.errors.connection, jstr.text),
            'parse_mode': 'HTML'
        }
        result = {
            'type': 'article',
            'id': str(jstr.status_code),
            'title': lang.errors.connection,
            'input_message_content': message,
            'description': jstr.text
        }
        results_json.append(result)

    jdat = json.loads(jstr.text)

    if not len(jdat['responseData']['results']) != 0:
        message = {
            'message_text': lang.errors.results,
            'parse_mode': 'HTML'
        }
        result = {
            'type': 'article',
            'id': str(jstr.status_code),
            'title': lang.errors.results,
            'input_message_content': message,
            'description': jstr.text
        }
        results_json.append(result)

    for item in jdat['responseData']['results']:
        message = {
            'message_text': item['unescapedUrl'],
            'parse_mode': 'HTML'
        }

        result = {
            'type': 'article',
            'id': item['cacheUrl'].split(':')[-2],
            'title': item['titleNoFormatting'],
            'url': item['url'],
            'input_message_content': message,
            'description': BeautifulSoup(item['content'], 'lxml').text,
            'thumb_url': 'http://fa2png.io/media/icons/fa-globe/96/16/673ab7_ffffff.png',
            'thumb_width': 128,
            'thumb_height': 128
        }
        
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(m, results)
