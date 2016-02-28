from core.utils import *

commands = [
    ('/cat', [])
]
description = 'Get a cat pic!'


def run(m):
    url = 'http://thecatapi.com/api/images/get'

    params = {
        'format': 'src',
        'api_key': config.keys.cat_api
    }

    jstr = requests.get(
        url,
        params=params,
    )

    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)

    photo = download(url)

    if photo:
        send_photo(m, photo)
    else:
        send_message(m, 'Error Downloading!')
