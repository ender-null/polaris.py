from polaris.utils import get_input, mp3_to_ogg, send_request, download, first_word, all_but_first_word


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.text_to_speech.commands
        self.description = self.bot.trans.plugins.text_to_speech.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        langs = [
            'af', 'aq', 'ar', 'hy', 'ca', 'zh', 'zh-cn', 'zh-tw', 'zh-yue',
            'hr', 'cs', 'da', 'nl', 'en-au', 'en-uk', 'en-us', 'eo',
            'fi', 'fr', 'de', 'el', 'ht', 'hu', 'is', 'id',
            'it', 'ja', 'ko', 'la', 'lv', 'mk', 'no', 'pl',
            'pt', 'pt-br', 'ro', 'ru', 'sr', 'sk', 'es', 'es-es',
            'es-us', 'sw', 'sv', 'ta', 'th', 'tr', 'vi', 'cy'
        ]

        for lang in langs:
            if first_word(input) == lang:
                language = lang
                text = all_but_first_word(input)
                break
            else:
                if self.bot.config.translation != 'default':
                    language = 'es-es'
                else:
                    language = 'en-us'
                text = input
                
        if not text:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
    
        url = 'http://translate.google.com/translate_tts'
        params = {
            'tl': language,
            'q': text,
            'ie': 'UTF-8',
            'total': len(text),
            'idx': 0,
            'client': 'tw-ob',
            'key': self.bot.config.api_keys.google_developer_console
        }
        headers = {
            "Referer": 'http://translate.google.com/',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.8 Safari/537.36"
        }

        file = download(url, params, headers)
        voice = mp3_to_ogg(file)

        if voice:
            return self.bot.send_message(m, voice, 'voice')
        else:
            return self.bot.send_message(m, self.bot.trans.errors.download_failed)
