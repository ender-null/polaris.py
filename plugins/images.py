from core.utils import *
import random
from requests.auth import HTTPBasicAuth

commands = {
    '/image': {('query', True)}
}
description = 'This command performs a Google Images search for the given query.'


def run(m):
    input = get_input(m)

    if not input:
        return send_msg(m, 'No input')

    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/Image'
    params = {
        'Query': "'" + input + "'",
        'Adult': "'Moderate'",
        '$format': 'json',
        '$top': '8'
    }
    auth = HTTPBasicAuth(config.keys.azure_key, config.keys.azure_key)

    jstr = requests.get(url, params=params, auth=auth)

    if jstr.status_code != 200:
        return send_msg(m, 'Connection Error!\n' + jstr.text)

    jdat = json.loads(jstr.text)

    if not len(jdat['d']['results']) != 0:
        return send_msg(m, 'No Results!')

    i = random.randint(1, len(jdat['d']['results'])) - 1

    result_url = jdat['d']['results'][i]['MediaUrl']
    caption = '"{0}"'.format(input)

    photo = download(result_url)

    if photo:
        send_pic(m, photo, caption)
    else:
        send_msg(m, 'Error Downloading!')
