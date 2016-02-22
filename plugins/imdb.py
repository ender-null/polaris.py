# -*- coding: utf-8 -*-

from utils import *

commands = ['^imdb']
parameters = {('text', True)}
description = 'Get info about a movie/series'
action = 'typing'

def run(msg):
    input = get_input(msg['text'])
    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://www.omdbapi.com/'
    params = {
        't': input,
        'plot': 'full',
        'r': 'json'
    }

    jstr = requests.get(
        url,
        params=params,
    )

    if jstr.status_code != 200:
        return send_error(msg, 'connection', jstr.status_code)

    jdat = json.loads(jstr.text)

    if not bool(jdat['Response']):
        return send_message(msg['chat']['id'], "Error, movie or series not found.")

    result_title = escape_markup(jdat['Title'])
    result_released = escape_markup(jdat['Released'])
    result_type = escape_markup(jdat['Type'])
    result_runtime = escape_markup(jdat['Runtime'])
    if result_type == 'series':
         result_runtime += ' per chapter.'
    result_genre = escape_markup(jdat['Genre'])
    result_imdbRating = escape_markup(jdat['imdbRating'])
    result_imdbVotes = escape_markup(jdat['imdbVotes'])
    result_imdbID = escape_markup(jdat['imdbID'])
    result_poster = escape_markup(jdat['Poster'])
    result_plot = escape_markup(jdat['Plot'])
    result_awards = escape_markup(jdat['Awards'])
    text = "[⁣]({})*Title*: {}\n*Rating*: {}/10 (_{}_)\n*Date*: {}\n*Duration*: {}\n\
*Genre*: {}\n\n*Plot*: {}\n\n*Type*: {}\n*Awards*: {}\n\n*Click* \
[here](www.imdb.com/title/{}) *for extra info.*".format(result_poster, result_title,
            result_imdbRating, result_imdbVotes, result_released, result_runtime,
            result_genre, result_plot, result_type, result_awards, result_imdbID)

    send_message(msg['chat']['id'], text, parse_mode='Markdown')