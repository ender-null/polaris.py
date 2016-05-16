from core.utils import *

commands = [
    ('/voicerss', ['language', 'text'])
]
description = 'Generates an audio file using Voice RSS API.'
shortcut = '/vr '

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
        return send_message(m, lang.errors.input)

    for v in langs:
        if first_word(input) == v:
            lang = v
            text = all_but_first_word(input)
            break
        else:
            lang = 'en-us'
            text = input

    url = 'https://api.voicerss.org'
    params = {
        'key': config.keys.voicerss,
        'src': text,
        'hl': lang,
        'r': '2',
        'c': 'ogg',
        'f': '16khz_16bit_stereo'
    }

    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        send_alert('%s\n%s' % (lang.errors.connection, jstr.text))
        return send_message(m, lang.errors.connection)

    voice = download(jstr.url, params=params)

    if voice:
        send_voice(m, voice)
    else:
        send_message(m, lang.errors.download)
        
def inline(m):
    input = get_input(m)

    for v in langs:
        if first_word(input) == v:
            lang = v
            text = all_but_first_word(input)
            break
        else:
            lang = 'en-us'
            text = input

    url = 'https://api.voicerss.org'
    params = {
        'key': config.keys.voicerss,
        'src': text,
        'hl': lang,
        'r': '2',
        'c': 'ogg',
        'f': '16khz_16bit_stereo'
    }

    jstr = requests.get(url, params=params)
    
    results = []
    
    if jstr.status_code != 200:
        result = {
            'type': 'article',
            'id': jstr.status_code,
            'title': lang.errors.connection,
            'input_message_content': '%s\n%s' % (lang.errors.connection, jstr.text),
            'description': jstr.text
        }
        results.append(result)
        return


    result = {
        'type': 'voice',
        'id': m.id,
        'voice_url': jstr.url,
        'title': text
    }
    results.append(result)

    answer_inline_query(m, results)

