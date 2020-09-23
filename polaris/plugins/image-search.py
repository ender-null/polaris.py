import re
from random import randint

import requests

from polaris.utils import (download, generate_command_help, get_input,
                           is_command, send_request)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.image_search.commands
        self.description = self.bot.trans.plugins.image_search.description

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
            # return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        url = 'https://duckduckgo.com/'
        params = {
            'q': input
        }
        res = requests.post(url, data=params)
        searchObj = re.search(r'vqd=([\d-]+)\&', res.text, re.M | re.I)
        if not searchObj:
            return self.bot.send_message(m, self.bot.trans.errors.unknown, extra={'format': 'HTML'})

        headers = {
            'authority': 'duckduckgo.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'sec-fetch-dest': 'empty',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://duckduckgo.com/',
            'accept-language': self.bot.config.locale + ';q=0.9',
        }

        params = (
            ('l', self.bot.config.locale),
            ('o', 'json'),
            ('q', input),
            ('vqd', searchObj.group(1)),
            ('f', ',,,'),
            ('p', '1'),
            ('v7exp', 'a'),
        )

        requestUrl = url + "i.js"

        data = send_request(requestUrl, headers=headers, params=params)

        if not data or not 'results' in data:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

        if len(data.results) == 0:
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        try:
            i = randint(0, len(data.results) - 1)
            photo = data.results[i].url
            caption = None  # data.results[i].title

        except Exception as e:
            self.bot.send_alert(e)
            photo = None

        if photo:
            return self.bot.send_message(m, photo, 'photo', extra={'caption': caption})
        else:
            return self.bot.send_message(m, self.bot.trans.errors.download_failed)
