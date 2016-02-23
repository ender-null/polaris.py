from core.shared import *
import requests, magic, mimetypes, tempfile, os


def send_msg(m, content, type='text'):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, content, type)
    else:
        message = Message(None, bot, m.receiver, content, type)
    outbox.put(message)


def send_exc(m, exception):
    message = Message(None, m.receiver, m.sender, 'Exception found!')
    outbox.put(message)


def get_input(text):
    if ' ' not in text:
        return False
    return text[text.find(" ") + 1:]


def first_word(text, i=1):
    try:
        word = text.split()[i - 1]
    except:
        return False
    return word


def all_but_first_word(text):
    if ' ' not in text:
        return False
    return text.replace(first_word(text) + ' ', '')


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
    file = open(f.name, 'rb')
    return file


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


def escape_markup(text):
    characters = ['_', '*', '[']

    for character in characters:
        text = text.replace(character, '\\' + character)

    return text
