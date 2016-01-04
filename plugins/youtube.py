# -*- coding: utf-8 -*-
from __main__ import *
from bs4 import BeautifulSoup

from utils import *

commands = [
    '^youtube',
    '^video',
    '^yt',
    '^ytget'
]

parameters = {('query', True)}

description = 'Returns the top results from YouTube.'
action = 'typing'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'type': 'video',
        'part': 'snippet',
        'maxResults': '1',
        'q': input,
        'key': config['api']['googledev']
    }

    jstr = requests.get(
            url,
            params=params,
    )

    if jstr.status_code != 200:
        return send_error(msg, 'connection', jstr.status_code)

    jdat = json.loads(jstr.text)

    if get_command(msg['text']) == 'ytget':
        url = 'http://www.youtubeinmp4.com/youtube.php'
        params = {
            'video': 'http://youtu.be/' + jdat['items'][0]['id']['videoId']
        }

        jstr = requests.get(url, params)
        soup = BeautifulSoup(jstr.text, 'lxml')

        download_link = soup.find(id='downloadMP4')['href']
        result_url = 'http://www.youtubeinmp4.com/' + download_link

        video = download(result_url)
        caption = jdat['items'][0]['snippet']['title']

        if video:
            send_video(msg['chat']['id'], video, caption=caption)
        else:
            send_error(msg, 'download')
    else:
        text = 'Watch "{}" on YouTube\nhttp://youtu.be/{}'.format(
                jdat['items'][0]['snippet']['title'],
                jdat['items'][0]['id']['videoId'])

        send_message(msg['chat']['id'], text)


def inline(qry):
    input = get_input(qry['query'])

    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'type': 'video',
        'part': 'snippet',
        'maxResults': '8',
        'q': input,
        'key': config['api']['googledev']
    }

    jdat = send_request(url, params)

    results_json = []
    for item in jdat['items']:
        text = 'Watch "{}" on YouTube\nhttp://youtu.be/{}'.format(
                item['snippet']['title'],
                item['id']['videoId'])

        result = {
            'type': 'article',
            'id': item['etag'].replace('"', ''),
            'title': item['snippet']['title'],
            'message_text': text,
            'description': item['snippet']['description'],
            'url': 'http://youtu.be/' + item['id']['videoId'],
            'thumb_url': item['snippet']['thumbnails']['default']['url']
        }
        results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(qry['id'], results)
