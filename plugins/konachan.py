# -*- coding: utf-8 -*-
from utilies import *
import random


commands = [
    '^konachan',
    '^kc ',
    '^k ',
    '^knsfw',
]

parameters = (('tags', True))

description = 'Gets an image from [Konachan](http://konachan.com), use *' + config['command_start'] + 'knsfw* to get potentially NSFW results.'
action = 'upload_photo'


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    tags = input
    if not get_command(msg['text']) == 'knsfw':
        tags += ' rating:s'

    url = 'http://konachan.com/post.json'
    params = {
        'limit': 100,
        'tags': tags
    }

    jdat = send_request(
        url,
        params=params
    )

    if len(jdat) < 1:
        return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['results'])

    i = random.randint(1, len(jdat))-1

    if not jdat:
        return send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['connection'].format(jstr.status_code), parse_mode="Markdown")

    result_url = jdat[i]['file_url']
    caption = str(len(jdat)) + ' results matching: "' + input + '"'

    photo = download(result_url)

    if photo:
        send_photo(msg['chat']['id'], photo, caption=caption)
    else:
        send_message(msg['chat']['id'], locale[get_locale(msg['chat']['id'])]['errors']['download'], parse_mode="Markdown")
