from core.utils import *

commands = [
    ('/youtube', ['query'])
]
description = 'Returns the top results from YouTube.'


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'type': 'video',
        'part': 'snippet',
        'maxResults': '1',
        'q': input,
        'key': config.keys.google_developer_console
    }

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)

    jdat = json.loads(jstr.text)

    text = 'Watch "{}" on YouTube\nhttp://youtu.be/{}'.format(
        jdat['items'][0]['snippet']['title'],
        jdat['items'][0]['id']['videoId'])

    send_message(m, text)
