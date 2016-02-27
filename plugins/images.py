from core.utils import *
from requests.auth import HTTPBasicAuth
import random, re

commands = [
    ('/image', ['query'])
]
description = 'This command performs a Google Images search for the given query.'

exts = {
    '.jpg$',
    '.jpeg$',
    '.gif$',
    '.png$',
    '.tif$',
    '.bmp$'
}

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

    is_real = False
    counter = 0
    while not is_real:
        counter = counter + 1
        if counter > 5 or jdat['d']['results'] == '0':
            return send_msg(m, 'No Results!')

        i = random.randint(1, len(jdat['d']['results']))-1
        result_url = jdat['d']['results'][i]['MediaUrl']
        caption = jdat['d']['results'][i]['DisplayUrl']
        # caption = jdat['d']['results'][i]['Title']  

        for v in exts:
            if re.compile(v).search(result_url):
                is_real = True  

    photo = download(result_url)

    if photo:
        send_pic(m, photo, caption)
    else:
        send_msg(m, 'Error Downloading!')
