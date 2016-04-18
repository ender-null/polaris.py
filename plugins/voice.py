from core.utils import *

commands = [
    ('/voice', ['language', 'text'])
]
description = 'Generates an audio file using Google Text-To-Speech API.'
shortcut = '/v '

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
            language = v
            text = all_but_first_word(input)
            break
        else:
            language = 'en-us'
            text = input

    url = 'http://translate.google.com/translate_tts'
    params = {
        'tl': language,
        'q': text,
        'ie': 'UTF-8',
        'total': len(text),
        'idx': 0,
        'client': 'tw-ob',
        'key': config.keys.google_developer_console
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
        send_alert('%s\n%s' % (lang.errors.connection, jstr.text))
        return send_message(m, lang.errors.connection)

    result_url = jstr.url
    voice = mp3_to_ogg(download(result_url, headers=headers, params=params))

    if voice:
        send_voice(m, voice)
    else:
        send_message(m, lang.errors.download)
        
def inline(m):
    input = get_input(m)

    for v in langs:
        if first_word(input) == v:
            language = v
            text = all_but_first_word(input)
            break
        else:
            language = 'en-us'
            text = input
            
    if not text:
        text = ''

    url = 'http://translate.google.com/translate_tts'
    params = {
        'tl': language,
        'q': text,
        'ie': 'UTF-8',
        'total': len(text),
        'idx': 0,
        'client': 'tw-ob',
        'key': config.keys.google_developer_console
    }

    jstr = requests.get(url, params=params)
    
    results_json = []
    
    if jstr.status_code != 200:
        message = {
            'message_text': '%s\n%s' % (lang.errors.connection, jstr.text),
            'parse_mode': 'HTML'
        }
        result = {
            'type': 'article',
            'id': str(jstr.status_code),
            'title': lang.errors.connection,
            'input_message_content': message,
            'description': jstr.text
        }
        results_json.append(result)
        return


    result = {
        'type': 'voice',
        'id': m.id,
        'voice_url': jstr.url,
        'title': text
    }
    results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(m, results)
