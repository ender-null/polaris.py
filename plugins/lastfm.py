from core.utils import *

commands = [
    ('/nowplaying', ['username'])
]
description = 'Returns what you are or were last listening to. If you specify a username, info will be returned for that username.'


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'user.getrecenttracks',
        'format': 'json',
        'limit': '1',
        'api_key': config.keys.lastfm,
        'user': username
    }

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        return send_message(m, '%s\n%s' % (lang.errors.connection, jstr.text))

    lastfm = json.loads(jstr.text)

    artist = lastfm['recenttracks']['track'][0]['artist']['#text']
    track = lastfm['recenttracks']['track'][0]['name']
    album = lastfm['recenttracks']['track'][0]['album']['#text']
    track_url = lastfm['recenttracks']['track'][0]['url']

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
        result += '`%s` is now playing:\n*Song*:_ %s_\n*Artist*:_ %s_' % (username, track, artist)
        if album:
            result += '\n*Album*:_ %s_' % (album)
    else:
        result += '`%s` last played (%s):\n*Song*:_ %s_\n*Artist*:_ %s_' % (username, date, track, artist)
        if album:
            result += '\n*Album*:_ %s_' % (album)

    # youtube
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'type': 'video',
        'part': 'snippet',
        'maxResults': '1',
        'q': '%s - %s - %s' % (track, album, artist),
        'key': config.keys.google_developer_console
    }

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        return send_message(m, '%s\n%s' % (lang.errors.connection, jstr.text))

    youtube = json.loads(jstr.text)

    result = '\n\nMight be this on YouTube\nhttp://youtu.be/%s' % (
        youtube['snippet']['title'],
        youtube['id']['videoId'])

    send_message(m, result, preview=False)
