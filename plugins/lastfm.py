# Made by zhantyzgz and fixed by me (luksireiku)
from core.utils import *

commands = [
    ('/nowplaying', ['username'])
]
description = 'Returns what you are or were last listening to. If you specify a username, info will be returned for that username.'
shortcut = '/np'


def run(m):
    username = get_input(m)

    if not username:
        if m.sender.username:
            username = m.sender.username
        else:
            return send_message(m, lang.errors.input)

    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'user.getrecenttracks',
        'format': 'json',
        'limit': '1',
        'api_key': config.keys.lastfm,
        'user': username
    }

    res = requests.get(url, params=params)

    if res.status_code != 200:
        return send_message(m, '%s\n%s' % (lang.errors.connection, res.text))

    lastfm = json.loads(res.text)
    
    if not 'recenttracks' in lastfm:
        return send_message(m, lang.errors.results)
    
    artist = lastfm['recenttracks']['track'][0]['artist']['#text'].title()
    track = lastfm['recenttracks']['track'][0]['name'].title()
    album = lastfm['recenttracks']['track'][0]['album']['#text'].title()
    track_url = lastfm['recenttracks']['track'][0]['url'].title()

    try:
        nowplaying = lastfm['recenttracks']['track'][0]['@attr']['nowplaying']
        if nowplaying == 'true':
            nowplaying = True
        else:
            nowplaying == False
    except:
        date = lastfm['recenttracks']['track'][0]['date']['#text']
        nowplaying = False

    result = ''
    if nowplaying:
        result += '`%s` is now playing:\n🎵 _%s_\n🗣 _%s_' % (username, track, artist)
        if album:
            result += '\n💽 _%s_' % (album)
    else:
        result += '`%s` last played \(%s):\n🎵 _%s_\n🗣 _%s_' % (username, date, track, artist)
        if album:
            result += '\n💽 _%s_' % (album)

    url_yt = 'https://www.googleapis.com/youtube/v3/search'
    params_yt = {
        'type': 'video',
        'part': 'snippet',
        'maxResults': '1',
        'q': '%s - %s - %s' % (track, artist, album),
        'key': config.keys.google_developer_console
    }

    res_yt = requests.get(url_yt, params=params_yt)

    if res_yt.status_code != 200:
        return send_message(m, '%s\n%s' % (lang.errors.connection, res_yt.text))

    youtube = json.loads(res_yt.text)

    if len(youtube['items']) > 0:
        result += '\n\n🎞 %s\nhttp://youtu.be/%s' % (
            youtube['items'][0]['snippet']['title'].replace('(','\('),
            youtube['items'][0]['id']['videoId'])

    send_message(m, result, markup='Markdown', preview=False)
