from polaris.utils import get_input, is_command, send_request, set_setting, get_setting
from polaris.types import AutosaveDict
from re import findall

class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.lastfm.commands
        self.description = self.bot.trans.plugins.lastfm.description

    # Plugin action #
    def run(self, m):
        if is_command(self, 1, m.content):
            username = get_input(m)

            if not username:
                username = get_setting(self.bot, m.sender.id, 'lastfm.username')
                if not username and m.sender.username:
                    username = m.sender.username
                if not username:
                    return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            url = 'http://ws.audioscrobbler.com/2.0/'
            params = {
                'method': 'user.getrecenttracks',
                'format': 'json',
                'limit': '1',
                'api_key': self.bot.config.api_keys.lastfm,
                'user': username
            }

            lastfm = send_request(url, params=params)


            # If the user didn't have any tracks or doesn't exist return No Results error. #
            try:
                last = lastfm.recenttracks.track[0]
            except:
                return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

            artist = last.artist['#text'].title()
            track = last.name.title()
            album = last.album['#text'].title()
            track_url = last.url

            try:
                nowplaying = last['@attr'].nowplaying
                if nowplaying == 'true':
                    nowplaying = True
                else:
                    nowplaying == False
            except:
                date = last.date['#text']
                nowplaying = False

            if nowplaying:
                text = self.bot.trans.plugins.lastfm.strings.now_playing % username
            else:
                text = self.bot.trans.plugins.lastfm.strings.last_played % username

            text += '\n🎵 <i>%s</i>\n💽 %s' % (track, artist)
            if album:
                text += ' - %s' % album


            # Gets the link of a Youtube video of the track. #
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'type': 'video',
                'part': 'snippet',
                'maxResults': '1',
                'q': '%s %s' % (track, artist),
                'key': self.bot.config.api_keys.google_developer_console
            }

            youtube = send_request(url, params=params)

            if not 'error' in youtube and len(youtube['items']) > 0:
                text += '\n\n🌐 %s\n%s\nhttps://youtu.be/%s' % (self.bot.trans.plugins.lastfm.strings.might_be, youtube['items'][0].snippet.title, youtube['items'][0].id.videoId)

            self.bot.send_message(m, text, extra={'format': 'HTML', 'preview': False})


        elif is_command(self, 2, m.content):
            input = get_input(m)
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            set_setting(self.bot, m.sender.id, 'lastfm.username', input)
            self.bot.send_message(m, self.bot.trans.plugins.lastfm.strings.username_set, extra={'format': 'HTML', 'preview': False})
