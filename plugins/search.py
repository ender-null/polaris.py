from core.utils import *
from requests.auth import HTTPBasicAuth

commands = [
    ('/search', ['query']),
    ('/snsfw', ['query'])
]
description = 'This command performs a Bing Web search for the given query.'
shortcut = ['/s ', None]

def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    url = 'https://api.datamarket.azure.com/Bing/Search/v1/Web'
    params = {
        'Query': "'" + input + "'",
        'Adult': "'Moderate'",
        '$format': 'json',
        '$top': '16'
    }
    auth = HTTPBasicAuth(config.keys.azure_key, config.keys.azure_key)

    if get_command(m) == 'insfw':
        params['Adult'] = "'Off'"

    jstr = requests.get(url, params=params, auth=auth)

    if jstr.status_code != 200:
        send_alert('%s\n%s' % (lang.errors.connection, jstr.text))
        return send_message(m, lang.errors.connection)

    jdat = json.loads(jstr.text)

    if not len(jdat['d']['results']) != 0:
        return send_message(m, lang.errors.results)

    message = '<b>Web results for</b> <i>%s</i>:' % input

    for result in jdat['d']['results']:
        if len(result['Title']) > 30:
            title = result['Title'][:27] + '...'
        else:
            title = result['Title']
        message += '\n • <a href="%s">%s</a>' % (result['Url'], title)

    send_message(m, message, markup='HTML')


def inline(m):
    input = get_input(m)
    query = ''
    caption = ''
    
    if not input:
        query = 'None'
    elif '|' in input and input[-1] != '|':
        query, caption = input.split('|')
    else:
        query = input

    url = 'https://api.datamarket.azure.com/Bing/Search/v1/Web'
    params = {
        'Query': "'%s'" % query,
        'Adult': "'Moderate'",
        '$format': 'json',
        '$top': '16'
    }
    auth = HTTPBasicAuth(config.keys.azure_key, config.keys.azure_key)

    if get_command(m) == 'snsfw':
        params['Adult'] = "'Off'"

    jstr = requests.get(url, params=params, auth=auth)
    
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

    if not len(jdat['d']['results']) != 0:
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

    for item in jdat['d']['results']:
        message = {
            'message_text': item['Url']
        }
        result = {
            'type': 'article',
            'id': item['ID'],
            'title': item['Title'],
            'input_message_content': message,
            'url': item['Url'],
            'description': item['Description'],
            'thumb_url': 'http://fa2png.io/media/icons/devicons-bing_small/96/32/ffffff_673ab7.png'
        }
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(m, results)
