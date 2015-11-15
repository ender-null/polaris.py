# -*- coding: utf-8 -*-
from utilies import *

commands = [
    '^image',
    '^img',
    '^i ',
    '^insfw'
]

parameters = (('query', True))

description = 'This command performs a Google Images search for the given query. One random top result is returned. Safe search is enabled by default; use *' + config['command_start'] + 'insfw* to get potentially NSFW results.'
action = 'upload_photo'

exts = {
    '.png$',
    '.jpg$',
    '.jpeg$',
    '.jpe$',
    '.gif$'
}


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://ajax.googleapis.com/ajax/services/search/images'
    params = {
        'v': '1.0',
        'rsz': 8,
        'safe': 'active',
        'q': input
    }

    if msg['text'].startswith(config['command_start'] + 'insfw'):
        del params['safe']

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        return send_message(msg['chat']['id'],
                            locale[get_locale(msg['chat']['id'])]['errors']['connection'].format(jstr.status_code),
                            parse_mode="Markdown")

    jdat = json.loads(jstr.text)

    if jdat['responseData']['results'] < 1:
        return send_message(msg['chat']['id'],
                            locale[get_locale(msg['chat']['id'])]['errors']['results'])

    is_real = False
    counter = 0
    while not is_real:
        counter = counter + 1
        if counter > 5 or len(jdat['responseData']['results']) < 1:
            return send_message(msg['chat']['id'],
                                locale[get_locale(msg['chat']['id'])]['errors']['results'],
                                parse_mode="Markdown")

        i = random.randint(1, len(jdat['responseData']['results']))-1

        result_url = jdat['responseData']['results'][i]['url']
        caption = '"' + input + '"'

        for v in exts:
            if re.compile(v).search(result_url):
                is_real = True

    photo = download(result_url)

    if photo:
        send_photo(msg['chat']['id'], photo, caption=caption)
    else:
        send_error(msg, 'download')
