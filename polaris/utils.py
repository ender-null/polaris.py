import json
import logging
import mimetypes
import os
import re
import subprocess
import tempfile
import traceback
from html.parser import HTMLParser
from re import IGNORECASE, compile
from time import sleep

import magic
import requests
from DictObject import DictObject
from firebase_admin import db

from polaris.types import AutosaveDict


def set_input(message, trigger):
    if message.type == 'text' or message.type == 'inline_query':
        # Get the text that is next to the pattern
        input_match = re.compile(
            trigger + '(.+)$', flags=re.IGNORECASE).search(message.content)
        if input_match and input_match.group(1):
            message.extra['input'] = input_match.group(1)

        # Get the text that is next to the pattern
        if message.reply and message.reply.content:
            input_match = re.compile(trigger + '(.+)$', flags=re.IGNORECASE).search(
                str(message.content) + ' ' + str(message.reply.content))
            if input_match and input_match.group(1):
                message.extra['input_reply'] = input_match.group(1)
        elif 'input' in message.extra:
            message.extra['input_reply'] = message.extra['input']

    return message


def get_input(message, ignore_reply=True):
    if message.extra:
        if ignore_reply and 'input' in message.extra:
            return message.extra['input']
        elif not ignore_reply and 'input_reply' in message.extra:
            return message.extra['input_reply']
    return None


def get_input_legacy(message, ignore_reply=True):
    if message.type == 'text' or message.type == 'inline_query':
        text = message.content
    else:
        return None

    if not ignore_reply and message.reply and message.reply.type == 'text':
        text += ' ' + message.reply.content

    if not ' ' in text:
        return None

    return text[text.find(" ") + 1:]


def get_command_index(plugin, text):
    if isinstance(text, str) and text.endswith('@' + plugin.bot.info.username) and ' ' not in text:
        text = text.replace('@' + plugin.bot.info.username, '')

    text = text.replace('/', plugin.bot.config['prefix'])

    for i in range(len(plugin.commands)):
        if is_command(plugin, i + 1, text):
            return i

    return None


def generate_command_help(plugin, text, show_hidden=True):
    index = get_command_index(plugin, text)
    if index == None:
        return None

    command = plugin.commands[index]
    if not show_hidden and 'hidden' in command and command['hidden']:
        return None

    doc = command['command'].replace('/', plugin.bot.config['prefix'])

    if 'parameters' in command and command['parameters']:
        for parameter in command['parameters']:
            name, required = list(parameter.items())[0]
            # Bold for required parameters, and italic for optional #
            if required:
                doc += ' <b>&lt;{}&gt;</b>'.format(name)
            else:
                doc += ' [{}]'.format(name)

    if 'description' in command:
        doc += '\n<i>{}</i>'.format(command['description'])

    return doc


def get_command(message, bot):
    if message.content.startswith(bot.config['prefix']):
        command = first_word(message.content).lstrip(bot.config['prefix'])
        return command.replace('@' + bot.username, '')
    elif message.type == 'inline_query':
        return first_word(message.content)
    else:
        return None


def is_command(plugin, number, text):
    if isinstance(text, str) and text.endswith('@' + plugin.bot.info.username) and ' ' not in text:
        text = text.replace('@' + plugin.bot.info.username, '')

    if number - 1 < len(plugin.commands) and 'command' in plugin.commands[number - 1]:
        if ((plugin.commands[number - 1]['command'] == '/start' and '/start' in text)
                or (plugin.commands[number - 1]['command'] == '/help' and '/help' in text)):
            trigger = plugin.commands[number - 1]['command'].replace('/', '^/')
        else:
            if text[0] == '/' and 'keep_default' in plugin.commands[number - 1] and plugin.commands[number - 1]['keep_default']:
                trigger = plugin.commands[number -
                                          1]['command'].replace('/', '^/')
            else:
                trigger = plugin.commands[number - 1]['command'].replace(
                    '/', plugin.bot.config['prefix']).lower()

        if 'parameters' not in plugin.commands[number - 1] and trigger.startswith('^'):
            trigger += '$'
        elif 'parameters' in plugin.commands[number - 1] and ' ' not in text:
            trigger += '$'
        elif 'parameters' in plugin.commands[number - 1] and ' ' in text:
            trigger += ' '

        if compile(trigger).search(text.lower()):
            return True

    if 'friendly' in plugin.commands[number - 1]:
        trigger = plugin.commands[number - 1]['friendly'].replace(
            '/', plugin.bot.config['prefix']).lower()
        if compile(trigger).search(text.lower()):
            return True

    if 'shortcut' in plugin.commands[number - 1]:
        trigger = plugin.commands[number - 1]['shortcut'].replace(
            '/', plugin.bot.config['prefix']).lower()
        if 'parameters' not in plugin.commands[number - 1] and trigger.startswith('^'):
            trigger += '$'
        elif 'parameters' in plugin.commands[number - 1] and ' ' not in text:
            trigger += '$'
        elif 'parameters' in plugin.commands[number - 1] and ' ' in text:
            trigger += ' '

        if compile(trigger).search(text.lower()):
            return True

    return False


def set_setting(bot, uid, key, value):
    if not isinstance(uid, str):
        uid = str(uid)

    if not uid in bot.settings:
        bot.settings[uid] = {}

    bot.settings[uid][key] = value
    set_data('settings/{}/{}'.format(bot.name, uid), bot.settings[uid])
    logging.info('END')


def get_setting(bot, uid, key):
    if not isinstance(uid, str):
        uid = str(uid)

    try:
        return bot.settings[uid][key]
    except:
        return None


def del_setting(bot, uid, key):
    if not isinstance(uid, str):
        uid = str(uid)

    del(bot.settings[uid][key])
    delete_data('settings/{}/{}/{}'.format(bot.name, uid, key))


def has_tag(bot, target, tag, return_match=False):
    if not isinstance(target, str):
        target = str(target)
    tags = []
    if target in bot.tags and '?' in tag:
        for target_tag in bot.tags[target]:
            if not target_tag:
                bot.tags[target].remove(target_tag)
                set_data('tags/{}/{}'.format(bot.name, target),
                         bot.tags[target])

            if target_tag and target_tag.startswith(tag.split('?')[0]):
                if return_match:
                    tags.append(target_tag)
                else:
                    return True

        if return_match:
            return tags
        else:
            return False

    elif target in bot.tags and tag in bot.tags[target]:
        return True

    else:
        return False


def set_tag(bot, target, tag):
    if not isinstance(target, str):
        target = str(target)

    if not target in bot.tags:
        bot.tags[target] = []

    if not tag in bot.tags[target]:
        bot.tags[target].append(tag)
        set_data('tags/{}/{}'.format(bot.name, target), bot.tags[target])
        return True


def del_tag(bot, target, tag):
    if not isinstance(target, str):
        target = str(target)

    if target in bot.tags and '?' in tag:
        for target_tag in bot.tags[target]:
            if target_tag.startswith(tag.split('?')[0]):
                bot.tags[target].remove(target_tag)
                set_data('tags/{}/{}'.format(bot.name, target),
                         bot.tags[target])
                break

    elif target in bot.tags and tag in bot.tags[target]:
        bot.tags[target].remove(tag)
        set_data('tags/{}/{}'.format(bot.name, target), bot.tags[target])


def is_group_admin(bot, uid, m=None):
    if m and m.conversation.id < 0:
        chat_admins = bot.get_chat_admins(m.conversation.id)
        for admin in chat_admins:
            if uid == str(admin.id):
                return True

    return False


def im_group_admin(bot, m):
    return is_group_admin(bot, str(bot.info.id), m)


def is_owner(bot, uid):
    if not isinstance(uid, str):
        uid = str(uid)

    return str(bot.config['owner']) == uid


def is_trusted(bot, uid, m=None):
    if not isinstance(uid, str):
        uid = str(uid)

    return has_tag(bot, uid, 'trusted')


def is_admin(bot, uid, m=None):
    if not isinstance(uid, str):
        uid = str(uid)

    if is_owner(bot, uid):
        return True

    elif is_trusted(bot, uid):
        return True

    elif is_group_admin(bot, uid, m):
        return True

    return False


def is_mod(bot, uid, gid):
    if not isinstance(uid, str):
        uid = str(uid)

    if has_tag(bot, uid, 'globalmod') or has_tag(bot, uid, 'mod:{}'.format(gid)):
        return True

    else:
        return False


def set_step(bot, target, plugin, step):
    if not isinstance(target, str):
        target = str(target)

    bot.steps[target] = {
        'plugin': plugin,
        'step': step
    }

    set_data('steps/{}/{}'.format(bot.name, target), bot.steps[target])


def get_step(bot, target):
    if not isinstance(target, str):
        target = str(target)

    if not bot.steps or not target in bot.steps:
        return None
    else:
        return bot.steps[target]


def cancel_steps(bot, target):
    if not isinstance(target, str):
        target = str(target)

    if target in bot.steps:
        del(bot.steps[target])
        delete_data('steps/{}/{}'.format(bot.name, target))


def get_full_name(bot, uid, include_username=True):
    if not isinstance(uid, str):
        uid = str(uid)
    name = ''
    if uid in bot.users:
        if 'first_name' in bot.users[uid] and bot.users[uid].first_name:
            name += ' ' + bot.users[uid].first_name
        if 'last_name' in bot.users[uid] and bot.users[uid].last_name:
            name += ' ' + bot.users[uid].last_name
        if include_username and 'username' in bot.users[uid] and bot.users[uid].username:
            name += ' (@' + bot.users[uid].username + ')'
    elif uid in bot.groups:
        name = bot.groups[uid].title

    else:
        name = '[UNKNOWN]'

    return name

def get_username(bot, uid, include_username=True):
    if not isinstance(uid, str):
        uid = str(uid)
    name = ''
    if uid in bot.users:
        if 'first_name' in bot.users[uid] and bot.users[uid].first_name:
            name += ' ' + bot.users[uid].first_name
        if 'last_name' in bot.users[uid] and bot.users[uid].last_name:
            name += ' ' + bot.users[uid].last_name
        if 'username' in bot.users[uid] and bot.users[uid].username:
            name = '@' + bot.users[uid].username
    elif uid in bot.groups:
        name = bot.groups[uid].title
        if 'username' in bot.groups[uid] and bot.groups[uid].username:
            name = '@' + bot.groups[uid].username

    else:
        name = '[UNKNOWN]'

    return name


def split_large_message(content, max_length):
    lines = content.splitlines()
    texts = []
    text = ''
    line_break = '\n'
    length = 0

    for line in lines:
        if (length + len(line) + len(line_break)) < max_length:
            text += line + line_break
            length += len(line) + len(line_break)
        else:
            texts.append(text)
            text = line + line_break
            length = len(line) + len(line_break)

    texts.append(text)

    return texts


def first_word(text, i=1):
    try:
        return text.split()[i - 1]
    except:
        return None


def all_but_first_word(text):
    if not text or ' ' not in text:
        return None
    return text.split(' ', 1)[1]


def last_word(text):
    if not text:
        return None
    return text.split()[-1]


def is_int(number):
    try:
        number = int(number)
        return True
    except:
        return False


def is_hex(number):
    try:
        number = int(number, 16)
        return True
    except:
        return False


def positive(number):
    if is_int(number):
        if int(number) < 0:
            return - int(number)
        else:
            return int(number)

    return number


def get_plugin_name(obj):
    return str(type(obj)).split('.')[2]


# Returns all plugin names from /polaris/plugins/ #
def load_plugin_list():
    plugin_list = []
    for plugin_name in os.listdir('polaris/plugins'):
        if plugin_name.endswith('.py'):
            plugin_list.append(plugin_name[:-3])
    return sorted(plugin_list)


def send_request(url, params=None, headers=None, files=None, data=None, post=False, parse=True, verify=True, bot=None, return_error_response=False):
    try:
        if post:
            r = requests.post(url, params=params, headers=headers,
                              files=files, data=data, timeout=100, verify=verify)
        else:
            r = requests.get(url, params=params, headers=headers,
                             files=files, data=data, timeout=100, verify=verify)
    except:
        logging.error('Error making request to: {}'.format(url))
        if bot:
            bot.send_alert('Error making request to: {}'.format(url))
        if verify:
            return send_request(url, params, headers, files, data, post, parse, False, bot)
        else:
            return None

    if r.status_code != 200:
        logging.error(r.text)
        if bot:
            bot.send_alert(r.text)

        while r.status_code == 429:
            sleep(5)
            return send_request(url, params, headers, files, data, post, parse, bot=bot)
    try:
        if parse:
            try:
                result = json.loads(r.text)
                if isinstance(result, dict):
                    return DictObject(result)
                return result
            except Exception as e:
                logging.error(r.text)
                catch_exception(e)
                return r.text

        else:
            return r.url
    except Exception as e:
        logging.error(r.text)
        catch_exception(e)
        return None


def get_coords(input, bot=None):
    lang = 'en'
    if bot and bot.config.translation != 'default':
        lang = 'es'

    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': input,
        'language': lang,
        'key': bot.config.api_keys.google_developer_console
    }

    data = send_request(url, params=params, bot=bot)
    if data.status != 'OK':
        logging.info(data)

    if data and len(data.results) > 0:
        locality = data.results[0].address_components[0].long_name
        for address in data.results[0].address_components:
            if 'country' in address['types']:
                country = address['long_name']

        return (data.status, (data['results'][0]['geometry']['location']['lat'],
                              data['results'][0]['geometry']['location']['lng'],
                              locality, country))
    else:
        return (data.status, (None, None, None, None))


def get_streetview(latitude, longitude, key, size='640x320', fov=90, heading=235, pitch=10):
    url = 'http://maps.googleapis.com/maps/api/streetview'
    params = {
        'size': size,
        'location': '{},{}'.format(latitude, longitude),
        'fov': fov,
        'heading': heading,
        'pitch': pitch,
        'key': key
    }

    return download(url, params=params)


def download(url, params=None, headers=None, method='get', extension=None, verify=True):
    try:
        if method == 'post':
            res = requests.post(url, params=params,
                                headers=headers, stream=True, verify=verify)
        else:
            res = requests.get(url, params=params,
                               headers=headers, stream=True, verify=verify)
        if not extension:
            extension = get_extension(url)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    except Exception as e:
        logging.error(e)
        if verify:
            return download(url, params, headers, method, extension, False)
        else:
            return None
        return None
    f.seek(0)
    if not extension:
        f.name = fix_extension(f.name)
    return f.name


def save_to_file(res):
    ext = os.path.splitext(res.url)[1].split('?')[0]
    f = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    for chunk in res.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
    f.seek(0)
    if not ext:
        f.name = fix_extension(f.name)
    return open(f.name, 'rb')


def get_extension(path):
    return os.path.splitext(path)[1].split('?')[0]


def fix_extension(file_path):
    type = magic.from_file(file_path, mime=True)
    extension = str(mimetypes.guess_extension(type, strict=False))
    if extension is not None:
        # I hate to have to use this s***
        if extension.endswith('jpe'):
            extension = extension.replace('jpe', 'jpg')
        os.rename(file_path, file_path + extension)
        return file_path + extension
    else:
        return file_path


def get_short_url(long_url, api_key):
    url = 'https://www.googleapis.com/urlshortener/v1/url'
    params = {'longUrl': long_url, 'key': api_key}
    headers = {'content-type': 'application/json'}

    res = send_request(url, params=params, headers=headers,
                       data=json.dumps(params), post=True)

    return res.id


def mp3_to_ogg(input):
    try:
        output = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg').name
        with open(os.devnull, "w") as DEVNULL:
            subprocess.check_call(
                ['ffmpeg', '-i', input, '-ac', '1', '-c:a',
                    'libopus', '-b:a', '16k', '-y', output],
                stdout=DEVNULL)

        return output
    except Exception as e:
        logging.info('ffmpeg -i ' + input +
                     '-ac 1 -c:a opus -b:a 16k -y ' + output)
        logging.error(e)
        return None


def fix_telegram_link(link):
    input_match = compile(
        r'(?i)(?:t|telegram|tlgrm)\.(?:me|dog)\/joinchat\/([a-zA-Z0-9\-]+)', flags=IGNORECASE).search(link)
    if input_match and input_match.group(1):
        fixed_link = 'https://t.me/joinchat/{}'.format(input_match.group(1))
        logging.info('fixed telegram link: {}'.format(fixed_link))
        return fixed_link
    return link


def escape_markdown(text):
    characters = ['_', '*', '[', ']', '`', '(', ')']
    for char in characters:
        text.replace(char, '\\' + char)

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


def replace_html(text):
    text = re.sub(r'&lt;', r'<', text, flags=re.MULTILINE)
    text = re.sub(r'&gt;', r'>', text, flags=re.MULTILINE)
    return text


def remove_html(text):
    text = re.sub('<[^<]+?>', '', text)
    text = replace_html(text)
    return text


def html_to_discord_markdown(text):
    replacements = [
        (r'<code class="language-([\w]+)">([\S\s]+)</code>', r'```\1\n\2```'),
        # (r'<a href=\"(.[^\<]+)\">(.[^\<]+)</a>', r'[\2](\1)'),
        (r'<a href=\"(.[^\<]+)\">(.[^\<]+)</a>', r'\1'),
        (r'<[/]?i>', r'_'),
        (r'<[/]?b>', r'**'),
        (r'<[/]?u>', r'__'),
        (r'<[/]?code>', r'`'),
        (r'<[/]?pre>', r'```')
    ]

    for pattern, sub in replacements:
        text = re.sub(pattern, sub, text, flags=re.MULTILINE)

    text = replace_html(text)
    return text


def get_target(bot, m, input):
    if input:
        target = first_word(input)
        if is_int(target):
            return str(target)

        elif target.startswith('@'):
            if bot.info.username.lower() == target[1:].lower():
                return str(bot.info.id)

            for uid in bot.users:
                if 'username' in bot.users[uid] and isinstance(bot.users[uid].username, str) and bot.users[uid].username.lower() == target[1:].lower():
                    return str(uid)

            for gid in bot.groups:
                if 'username' in bot.groups[gid] and isinstance(bot.groups[gid].username, str) and bot.groups[gid].username.lower() == target[1:].lower():
                    return str(uid)

        elif target.startswith('<@'):
            return re.sub(r'<@!?([\d]+)>', r'\1', target, flags=re.MULTILINE)

        elif target == '-g':
            return str(m.conversation.id)

        else:
            for gid in bot.groups:
                if re.compile(target, flags=re.IGNORECASE).search(bot.groups[gid].title):
                    return gid

            for uid in bot.users:
                name = ''
                if 'first_name' in bot.users[uid]:
                    name += bot.users[uid].first_name
                if 'last_name' in bot.users[uid]:
                    name += bot.users[uid].last_name
                if re.compile(target, flags=re.IGNORECASE).search(name):
                    return uid

    elif m.reply:
        return str(m.reply.sender.id)

    else:
        return str(m.sender.id)


def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def init_if_empty(_dict):
    if _dict:
        return DictObject(_dict)
    else:
        return {}


def catch_exception(exception, bot=None):
    logging.info('Catched exception: ' + exception.__class__.__name__)
    logging.exception(traceback.format_exc())
    if bot:
        bot.send_alert(traceback.format_exc())


def wait_until_received(path):
    while True:
        try:
            data = init_if_empty(db.reference(path).get())
            break
        except:
            continue
    return data


def set_data(path, value):
    while True:
        try:
            db.reference(path).set(value)
            break
        except:
            continue


def update_data(path, value):
    while True:
        try:
            db.reference(path).update(value)
            break
        except:
            continue


def delete_data(path):
    while True:
        try:
            db.reference(path).delete()
            break
        except:
            continue


def set_logger(debug=False):
    logFormatterConsole = logging.Formatter(
        "[%(processName)-11.11s]  %(message)s")
    logFormatterFile = logging.Formatter(
        "%(asctime)s [%(processName)-11.11s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    if debug:
        rootLogger.setLevel(logging.DEBUG)
    else:
        rootLogger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler("bot.log", mode='w')
    fileHandler.setFormatter(logFormatterFile)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatterConsole)
    rootLogger.addHandler(consoleHandler)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("polaris.types").getChild(
        'AutosaveDict').setLevel(logging.ERROR)
