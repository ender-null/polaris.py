from core.utils import *

commands = [
    ('/echo', ['text'])
]
description = 'Repeat a string.'


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    send_message(m, latcyr(input), markup='Markdown', preview=False)


def inline(m):
    input = get_input(m)

    results_json = []
    result = {
        'type': 'article',
        'id': input,
        'title': 'Echo',
        'message_text': input,
        'description': input,
        'thumb_url': 'http://fa2png.io/media/icons/fa-comment/96/16/673ab7_ffffff.png',
        'parse_mode': 'Markdown'
    }
    results_json.append(result)

    results = json.dumps(results_json)
    answer_inline_query(m, results)
