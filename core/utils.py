from core.shared import *
from core.shortcuts import *
import requests, magic, mimetypes, tempfile, os, subprocess


def get_input(message):
    if message.type != 'text':
        return None
    else:
        text = message.content

    if message.reply and message.reply.type == 'text':
        text += ' ' + message.reply.content

    if not ' ' in text:
        return None

    return text[text.find(" ") + 1:]


def get_command(message):
    if message.content.startswith(config.start):
        command = message.content.split(' ')[0].lstrip(config.start)
        command = command.replace('@' + bot.username, '')
        return command
    else:
        return None


def first_word(text, i=1):
    try:
        return text.split()[i - 1]
    except:
        return False


def all_but_first_word(text):
    if ' ' not in text:
        return False
    return text.lstrip(first_word(text))


def last_word(text):
    if ' ' not in text:
        return False
    return text.split()[-1]


def is_int(number):
    try:
        number = int(number)
        return True
    except ValueError:
        return False


def download(url, params=None, headers=None):
    try:
        jstr = requests.get(url, params=params, headers=headers, stream=True)
        ext = os.path.splitext(url)[1]
        f = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        for chunk in jstr.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    except IOError as e:
        return None
    f.seek(0)
    if not ext:
        f.name = fix_extension(f.name)
    return open(f.name, 'rb')


def fix_extension(file_path):
    type = magic.from_file(file_path, mime=True).decode("utf-8")
    extension = str(mimetypes.guess_extension(type, strict=False))
    if extension is not None:
        # I hate to have to use this s***, f*** jpe
        if '.jpe' in extension:
            extension = extension.replace('jpe', 'jpg')
        os.rename(file_path, file_path + extension)
        return file_path + extension
    else:
        return file_path


def send_request(url, params=None, headers=None, files=None, data=None):
    jstr = requests.get(url, params=params, headers=headers, files=files, data=data)

    if jstr.status_code != 200:
        print(jstr.text)
        return False

    return json.loads(jstr.text)


def get_coords(input):
    url = 'http://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': input}

    jdat = send_request(url, params=params)

    if not jdat or jdat['status'] == 'ZERO_RESULTS':
        return False, False, False, False

    locality = jdat['results'][0]['address_components'][0]['long_name']
    for address in jdat['results'][0]['address_components']:
        if 'country' in address['types']:
            country = address['long_name']

    return (jdat['results'][0]['geometry']['location']['lat'],
            jdat['results'][0]['geometry']['location']['lng'],
            locality, country)


def get_short_url(long_url):
    url = 'https://www.googleapis.com/urlshortener/v1/url'
    params = {'longUrl': long_url, 'key': config.keys.google_developer_console}
    headers = {'content-type': 'application/json'}

    jstr = requests.post(url, data=json.dumps(params), headers=headers)

    if jstr.status_code != 200:
        print(jstr.text)
        return False

    jdat = json.loads(jstr.text)

    return (jdat['id'])


def mp3_to_ogg(original):
    converted = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
    conv = subprocess.Popen(
        ['avconv', '-i', original.name, '-ac', '1', '-c:a', 'opus', '-b:a', '16k', '-y', converted.name],
        stdout=subprocess.PIPE)

    while True:
        data = conv.stdout.read(1024 * 100)
        if not data:
            break
        converted.write(data)

    return open(converted.name, 'rb')


def escape_markdown(text):
    characters = ['_', '*', '[']

    for character in characters:
        text = text.replace(character, '\\' + character)

    return text


def remove_markdown(text):
    characters = ['_', '*', '[', ']', '`', '(', ')', '\\']
    aux = list()
    for x in range(len(text)):
        if x > 0 and text[x] in characters and text[x - 1] != '\\':
            pass
        else:
            aux.append(text[x])
    return ''.join(aux)


def is_admin(id):
    if id == config.owner:
        return True
    else:
        return False
