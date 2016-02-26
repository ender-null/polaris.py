from core.shared import *
import requests, magic, mimetypes, tempfile, os, traceback, sys, subprocess


def send_msg(m, text, preview=False, markup=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, text, 'text', markup=markup, extra=preview)
    else:
        message = Message(None, bot, m.receiver, text, 'text', markup=markup, extra=preview)
    outbox.put(message)


def send_pic(m, photo, caption=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, photo, 'photo', extra=caption)
    else:
        message = Message(None, bot, m.receiver, photo, 'photo', extra=caption)
    outbox.put(message)


def send_doc(m, document):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, document, 'document')
    else:
        message = Message(None, bot, m.receiver, document, 'document')
    outbox.put(message)


def send_vid(m, video, caption=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, video, 'video', extra=caption)
    else:
        message = Message(None, bot, m.receiver, video, 'video', extra=caption)
    outbox.put(message)


def send_aud(m, audio, title=None):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, audio, 'audio', extra=title)
    else:
        message = Message(None, bot, m.receiver, audio, 'audio', extra=title)
    outbox.put(message)


def send_vce(m, voice):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, voice, 'voice')
    else:
        message = Message(None, bot, m.receiver, voice, 'voice')
    outbox.put(message)


def send_stk(m, sticker):
    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, sticker, 'sticker')
    else:
        message = Message(None, bot, m.receiver, sticker, 'sticker')
    outbox.put(message)


def send_exc(m, exception):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb, 4)
    message = '\n`' + str(exc_type) + '`'
    message += '\n\n`' + str(exc_obj) + '`'
    for row in tb:
        message += '\n'
        for val in row:
            message += '`' + str(val) + '`\n'

    if m.receiver.id > 0:
        message = Message(None, m.receiver, m.sender, message, markup='Markdown')
    else:
        message = Message(None, bot, m.receiver, message, markup='Markdown')
    outbox.put(message)


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

def mp3_to_ogg(original):
    converted = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
    conv = subprocess.Popen(['avconv', '-i', original.name, '-ac', '1', '-c:a', 'opus', '-b:a', '16k', '-y', converted.name], stdout=subprocess.PIPE)
    
    while True:
        data = conv.stdout.read(1024 * 100)
        if not data:
            break
        converted.write(data)

    return open(converted.name, 'rb')


def escape_markup(text):
    characters = ['_', '*', '[']

    for character in characters:
        text = text.replace(character, '\\' + character)

    return text

def is_admin(id):
    if id == config.owner:
        return True
    else:
        return False
