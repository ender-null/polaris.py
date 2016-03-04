from core.utils import *

commands = [
    ('/voice', ['language', 'text'])
]
description = 'Generates an audio file using Google Text-To-Speech API.'

langs = [
    'af', 'aq', 'ar', 'hy', 'ca', 'zh', 'zh-cn', 'zh-tw', 'zh-yue',
    'hr', 'cs', 'da', 'nl', 'en-au', 'en-uk', 'en-us', 'eo',
    'fi', 'fr', 'de', 'el', 'ht', 'hu', 'is', 'id',
    'it', 'ja', 'ko', 'la', 'lv', 'mk', 'no', 'pl',
    'pt', 'pt-br', 'ro', 'ru', 'sr', 'sk', 'es', 'es-es',
    'es-us', 'sw', 'sv', 'ta', 'th', 'tr', 'vi', 'cy'
]


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    for v in langs:
        if first_word(input) == v:
            lang = v
            text = all_but_first_word(input)
            break
        else:
            lang = 'en'
            text = input

    url = 'http://translate.google.com/translate_tts'
    params = {
        'tl': lang,
        'q': text,
        'ie': 'UTF-8',
        'total': len(text),
        'idx': 0,
        'client': 'tw-ob',
    }
    headers = {
        "Referer": 'http://translate.google.com/',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.8 Safari/537.36"
    }

    jstr = requests.get(
        url,
        params=params,
        headers=headers
    )

    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)

    result_url = jstr.url
    voice = mp3_to_ogg(download(result_url, headers=headers, params=params))

    if voice:
        send_voice(m, voice)
    else:
        send_message(m, 'Error Downloading!')
