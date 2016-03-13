from core.utils import *

commands = [
    ('/youtube', ['query'])
]
description = 'Returns the top results from YouTube.'
shortcut = '/yt '


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

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
        send_exception(m, '%s\n%s' % (lang.errors.connection, jstr.text))
        return send_message(m, lang.errors.connection)

    jdat = json.loads(jstr.text)

    text = 'Watch "%s" on YouTube\nhttp://youtu.be/%s' % (
        jdat['items'][0]['snippet']['title'],
        jdat['items'][0]['id']['videoId'])

    send_message(m, text, preview=True)


def inline(m):
    input = get_input(m)

    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'type': 'video',
        'part': 'snippet',
        'maxResults': '8',
        'q': input,
        'key': config.keys.google_developer_console
    }

    jdat = send_request(url, params)

    results_json = []
    for item in jdat['items']:
        text = 'Watch "%s" on YouTube\nhttp://youtu.be/%s' % (
            item['snippet']['title'],
            item['id']['videoId'])

        url = 'https://www.googleapis.com/youtube/v3/videos'
        params = {
            'part': 'contentDetails',
            'id': item['id']['videoId'],
            'key': config.keys.google_developer_console
        }

        duration_iso = send_request(url, params)['items'][0]['contentDetails']['duration'].lower()

        week = 0
        day = 0
        hour = 0
        min = 0
        sec = 0

        value = ''
        for c in duration_iso:
            if c.isdigit():
                value += c
                continue

            elif c == 'p':
                pass
            elif c == 't':
                pass
            elif c == 'w':
                week = int(value) * 604800
            elif c == 'd':
                day = int(value) * 86400
            elif c == 'h':
                hour = int(value) * 3600
            elif c == 'm':
                min = int(value) * 60
            elif c == 's':
                sec = int(value)

            value = ''

        duration = week + day + hour + min + sec

        result = {
            'type': 'video',
            'id': item['etag'].replace('"', ''),
            'title': item['snippet']['title'],
            'message_text': text,
            'description': item['snippet']['description'],
            'mime_type': 'text/html',
            'video_url': 'http://youtu.be/' + item['id']['videoId'],
            'video_duration': duration,
            'thumb_url': item['snippet']['thumbnails']['default']['url']
        }
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(m, results)
