from core.bindings import *
import requests, magic, mimetypes, tempfile, os, subprocess


def get_input(message, ignore_reply=False):
    if message.type == 'text' or message.type == 'inline_query':
        text = message.content
    else:
        return None

    if not ignore_reply and message.reply and message.reply.type == 'text':
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


def save_json(path, data, hide=False):
    try:
        with open(path, 'w') as f:
            if not hide:
                print('\t[OK] ' + path)
            json.dump(data, f, sort_keys=True, indent=4)
    except:
        print('\t%s[Failed] %s%s' % (Colors.FAIL, path, Colors.ENDC))
        pass


def load_json(path, hide=False):
    try:
        with open(path, 'r') as f:
            if not hide:
                print('\t[OK] ' + path)
            return json.load(f, object_pairs_hook=OrderedDict)
    except:
        print('\t[Failed] ' + path)
        return {}


def download(url, params=None, headers=None, method='get'):
    try:
        if method == 'post':
            res = requests.post(url, params=params, headers=headers, stream=True)
        else:
            res = requests.get(url, params=params, headers=headers, stream=True)
        ext = os.path.splitext(url)[1].split('?')[0]
        f = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        for chunk in res.iter_content(chunk_size=1024):
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
    res = requests.get(url, params=params, headers=headers, files=files, data=data)

    if res.status_code != 200:
        print(res.text)
        return False

    return json.loads(res.text)


def get_coords(input):
    url = 'http://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': input}

    data = send_request(url, params=params)

    if not data or data['status'] == 'ZERO_RESULTS':
        return False, False, False, False

    locality = data['results'][0]['address_components'][0]['long_name']
    for address in data['results'][0]['address_components']:
        if 'country' in address['types']:
            country = address['long_name']

    return (data['results'][0]['geometry']['location']['lat'],
            data['results'][0]['geometry']['location']['lng'],
            locality, country)


def get_short_url(long_url):
    url = 'https://www.googleapis.com/urlshortener/v1/url?longUrl=' + long_url + '&key=' + config.keys.google_developer_console
    params = {'longUrl': long_url, 'key': config.keys.google_developer_console}
    headers = {'content-type': 'application/json'}

    res = requests.post(url, data=json.dumps(params), headers=headers)

    if res.status_code != 200:
        return False

    data = json.loads(res.text)

    return (data['id'])


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
    characters = ['_', '*', '[', '`', '(', '\\']
    aux = list()
    for x in range(len(text)):
        if x >= 0 and text[x] in characters and text[x - 1] != '\\':
            pass
        else:
            aux.append(text[x])
    return ''.join(aux)


def is_admin(id):
    if id == config.owner or has_tag(id, 'admin'):
        return True
    else:
        return False


def is_trusted(id):
    if is_admin(id) or has_tag(id, 'trusted'):
        return True
    else:
        return False


def is_mod(id, gid):
    if is_admin(id) or has_tag(id, 'globalmod') or has_tag(id, 'mod:%s' % str(gid)[1:]):
        return True
    else:
        return False


def set_tag(id, tag):
    uid = str(id)
    message = ''
    if not uid in tags.list:
        tags.list[uid] = []

    if not tag in tags.list[uid]:
        tags.list[uid].append(tag)
        message += '\'%s\' ' % tag
    
    tags.save(tags)
    return message


def rem_tag(id, tag):
    uid = str(id)
    message = ''
    if not uid in tags.list:
        return message

    if tag in tags.list[uid]:
        tags.list[uid].remove(tag)
        message += '-\'%s\' ' % tag

    tags.save(tags)
    return message


def has_tag(id, tag):
    uid = str(id)
    if uid in tags.list and tag in tags.list[uid]:
        return True
    else:
        return False
