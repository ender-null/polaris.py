# -*- coding: utf-8 -*-
from collections import OrderedDict
from bindings import *
import datetime
import importlib
import json
import magic
import mimetypes
import sys
import os
import re
import requests
import tempfile
import time
import urllib
import traceback


def bot_init():
    print('Loading config... ')
    global config
    config = load_json('data/config.json')

    global groups
    groups = load_json('data/groups.json')
    
    global users
    users = load_json('data/users.json')

    global locale
    locale = OrderedDict()
    for file in config['locales']:
        locale[file] = load_json('locale/' + file + '.json')

    print('\nGetting bot data...')
    global bot
    bot = get_me()
    while not bot:
        print('\tFailure getting bot data. Trying again...')
        bot = get_me()
    bot = bot['result']
    print('\tFirst name:\t' + bot['first_name'])
    print('\tUsername:\t' + bot['username'])
    print('\tUser id:\t' + str(bot['id']))

    print('\nLoading plugins...')
    global plugins
    plugins = OrderedDict()
    plugins = load_plugins()

    global is_started
    is_started = True
    print('\n' + bot['first_name'] + ' is started!')


def on_message_receive(msg):
    if config['ignore']['old_messages'] and msg['date'] < now() - 10:
        return
    if config['ignore']['media'] and 'text' not in msg:
        return

    if 'text' not in msg:
        msg['text'] = ''

    # Adds the locale to the message
    #msg['locale'] = get_locale(msg['chat']['id']

    for i, plugin in plugins.items():
        more = True
        if hasattr(plugin, 'process'):
            plugin.process(msg)

        if hasattr(plugin, 'commands'):
            for command in plugin.commands:
                trigger = command.replace("^", "^" + config['command_start'])
                # trigger = tag_replace(trigger, msg)
                if re.compile(trigger).search(msg['text'].lower()):
                    try:
                        if hasattr(plugin, 'action'):
                            send_chat_action(msg['chat']['id'], plugin.action)
                        plugin.run(msg)
                    except Exception as e:
                        send_error(msg, 'exception')
                        send_exception(e)

                    more = False
                    break

        if hasattr(plugin, 'stop') and plugin.stop:
            more = False

        if not more:
            break


def load_plugins():
    for plugin in config['plugins']:
        try:
            plugins[plugin] = importlib.import_module('plugins.' + plugin)
            print('\t[OK] ' + plugin)
        except Exception as e:
            print('\t[Failed] ' + plugin + ': ' + str(e))

    print('\n\tLoaded: ' + str(len(plugins)) + '/' + str(len(config['plugins'])))
    return plugins


def save_json(path, data, hide=False):
    try:
        with open(path, 'w') as f:
            if not hide:
                print('\t[OK] ' + path)
            json.dump(data, f, sort_keys=True, indent=4)
    except:
        print(colored.red('\t[Failed] ' + path))
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


def now():
    return time.mktime(datetime.datetime.now().timetuple())


def get_command(text):
    if text.startswith(config['command_start']):
        command = text.split(' ')[0].lstrip(config['command_start'])
        command = command.replace('@' + bot['username'], '')
        return command


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
    url = 'https://www.googleapis.com/urlshortener/v1/url?longUrl=' + long_url + '&key=' + config['api']['googledev']
    params = {'longUrl': long_url, 'key': config['api']['googledev']}
    headers = {'content-type': 'application/json'}

    jstr = requests.post(url, data=json.dumps(params), headers=headers)

    if jstr.status_code != 200:
        return False

    jdat = json.loads(jstr.text)

    return (jdat['id'])


def get_locale(chat_id):
    if str(chat_id) in groups:
        return groups[str(chat_id)]['locale']
    else:
        return 'default'


def loc(chat_id):
    if str(chat_id) in groups:
        loc = groups[str(chat_id)]['locale']
        return locale[loc]
    else:
        return locale['default']


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
    url = urllib.pathname2url(file_path)
    type = magic.from_file(file_path, mime=True)
    extension = mimetypes.guess_extension(type, strict=False)
    if extension is not None:
        # I hate to have to use this s***, f*** jpe
        if '.jpe' in extension:
            extension = extension.replace('jpe', 'jpg')
        os.rename(file_path, file_path + extension)
        return file_path + extension
    else:
        return file_path


def tag_replace(text, msg=False):
    dt = datetime.datetime.now()
    if msg:
        loc = get_locale(msg['chat']['id'])
    else:
        loc = 'default'

    if dt.hour >= 5 and dt.hour < 12:
        greeting = locale[loc]['greeting']['morning']
    elif dt.hour <= 12 and dt.hour < 17:
        greeting = locale[loc]['greeting']['afternoon']
    elif dt.hour <= 17 and dt.hour < 21:
        greeting = locale[loc]['greeting']['evening']
    else:
        greeting = locale[loc]['greeting']['night']

    if dt.hour >= 5 and dt.hour < 12:
        goodbye = locale[loc]['goodbye']['morning']
    elif dt.hour <= 12 and dt.hour < 17:
        goodbye = locale[loc]['goodbye']['afternoon']
    elif dt.hour <= 17 and dt.hour < 21:
        goodbye = locale[loc]['goodbye']['evening']
    else:
        goodbye = locale[loc]['goodbye']['night']

    tags = {
        '#BOT_FIRSTNAME': escape_markup(bot['first_name']),
        '#BOT_USERNAME': escape_markup(bot['username']),
        '#GREETING': greeting,
        '#GOODBYE': goodbye,
        '#BOT_NAME_LOWER': escape_markup(bot['first_name'].split('-')[0].lower()),
        '#BOT_NAME': escape_markup(bot['first_name'].split('-')[0]),
        '    ': '',
    }

    if msg:
        tags['#FROM_FIRSTNAME'] = msg['from']['first_name']

    for k, v in tags.items():
        if k in text:
            text = text.replace(k, v)
    return text


def escape_markup(text):
    characters = ['_', '*', '[']

    for character in characters:
        text = text.replace(character, '\\' + character)

    return text


def delete_markup(text):
    characters = ['_', '*', '[', ']', '(', ')', '`']

    for character in characters:
        text = text.replace(character, '')

    return text


def get_doc(commands, parameters, description):
    doc = commands[0].replace('^', config['command_start'])
    if parameters:
        doc += format_parameters(parameters)
    doc += '\n' + description
    return doc


def format_parameters(parameters):
    formated_parameters = ''
    for parameter, required in parameters:
        if required:
            formated_parameters += ' *<' + parameter + '>*'
        else:
            formated_parameters += ' \[' + parameter + ']'
    return formated_parameters


def is_admin(msg):
    if msg['from']['id'] in config['admin']:
        return True
    else:
        return False


def is_mod(msg):
    if (is_admin(msg) or
                msg['from']['id'] in groups[str(msg['chat']['id'])]['mods']):

        return True
    else:
        return False


def get_size(number):
    size = ''
    unit = 0

    units = [
        '',
        'K',
        'M',
        'G',
        'T'
    ]

    while (number > 1024):
        number = number / 1024
        unit = unit + 1

    return str(number), units[unit]

def line(alt=False):
    if alt:
        return u'\n—————————————————————————\n'
    else:
        return u'\n`—————————————————————————`\n'

def send_error(msg, error_type, status_code=200):
    loc = get_locale(msg['chat']['id'])
    message = locale[loc]['errors'][error_type]
    if status_code != 200:
        message += '\n\t_Status code: ' + status_code + '_'
    send_message(msg['chat']['id'], message)


def send_alert(message):
    for group in groups.items():
        if group[1]['special'] == 'alerts':
            send_message(group[0], message, parse_mode="Markdown")


def send_exception(exception):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb, 4)
    message = '\n`' + str(exc_type) + '`'
    message += '\n\n`' + str(exc_obj) + '`'
    for row in tb:
        message += line()
        for val in row:
            message += '`' + str(val) + '`\n'
    send_alert(message)
