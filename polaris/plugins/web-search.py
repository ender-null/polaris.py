import logging
import re

import requests
from bs4 import BeautifulSoup

from polaris.utils import get_input, is_command, remove_html, send_request


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.web_search.commands

    # Plugin action #
    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

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

        requestUrl = url + "d.js"

        data = send_request(requestUrl, headers=headers, params=params)
        logging.info(data)

        if not data or not 'results' in data:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

        if len(data.results) == 0:
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        if not is_command(self, 2, m.content):
            text = self.bot.trans.plugins.web_search.strings.results % input
            limit = 8
            for item in data.results:
                if 't' in item:
                    logging.info(item['t'])
                    item['t'] = remove_html(item['t'])
                    if len(item['t']) > 26:
                        item['t'] = item['t'][:23] + '...'
                    text += '\n • <a href="%s">%s</a>' % (
                        item['u'], item['t'])
                    limit -= 1
                    if limit <= 0:
                        break

            self.bot.send_message(
                m, text, extra={'format': 'HTML', 'preview': False})

        else:
            text = data.results[0]['u']

            self.bot.send_message(
                m, text, extra={'format': 'HTML', 'preview': True})
