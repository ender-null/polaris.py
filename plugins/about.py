# -*- coding: utf-8 -*-
from utils import *
import platform
import subprocess
import psutil


commands = [
    '^about',
    '^system',
    '^start',
    '/start'
]

description = 'Info about *' + bot['first_name'] + '*'
action = 'typing'


def run(msg):
    header = 'Hi! I\'m *#BOT_FIRSTNAME*'
    header += '\nNice to meet you.'

    help = '\nUse ' + config['command_start'] + 'help for a list of commands.'
    license = '\n*#BOT_FIRSTNAME* uses *Polaris* which is licensed under the *GPLv2*.'
    source = '\n[Source Code on Github](https://github.com/luksireiku/polaris)'
    channel = '\nChannel: @PolarisUpdates'
    group = '\nJoin [Society of Polaris](https://telegram.me/joinchat/B09roADwf_8-9zMfxniOpA)!'
    stats = '\nUsers: {0}\nGroups: {1}'.format(len(users), len(groups))

    if get_command(msg['text']) == 'about':
        about = header + '\n' + license + source + '\n' + stats + '\n' + channel + group
        about = tag_replace(about, msg)

        send_message(msg['chat']['id'], about, disable_web_page_preview=True, parse_mode="Markdown")

    elif get_command(msg['text']) == 'system':
        running = '\n*Running on*:\n'
        running += '\t*System*: {0}\n'.format(subprocess.getoutput('head -n1 /etc/issue | cut -d " " -f -3'))
        running += '\t*Kernel*: {0}\n'.format(subprocess.getoutput('uname -rs'))
        running += '\t*CPU*: {0}\n'.format(subprocess.getoutput('cat /proc/cpuinfo | grep "model name" | tr -s " " | cut -d " " -f 3-'))
        running += '\t*RAM*: {0}MB ({1}% used)\n'.format(int(psutil.virtual_memory()[0] / 1000 / 1000), psutil.virtual_memory()[2])
        running += '\t*Python*: {0} ({1})\n'.format(str(platform.python_version()), str(platform.python_compiler()))
        running += '\t*Time*: {0}\n'.format(time.strftime("%c"))
        running += '\t*Uptime*: {0}\n'.format(subprocess.getoutput('uptime -p'))

        send_message(msg['chat']['id'], running, parse_mode="Markdown")

    else:
        start = tag_replace(header, msg)

        send_message(msg['chat']['id'], start, parse_mode="Markdown")
