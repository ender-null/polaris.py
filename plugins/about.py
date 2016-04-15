from core.utils import *

commands = [
    ('/about', [])
]
description = 'Info about <i>%s</i>' % bot.first_name


def run(m):
    header = 'Hi! I\'m <b>%s</b>!\nNice to meet you.' % bot.first_name
    help = '\nUse %shelp for a list of commands.' % config.start
    license = '\nUsing <code>sakubo</code> branch of <b>Polaris</b>, licensed under the <b>GPLv2</b>.'
    source = '\n<a href="https://github.com/luksireiku/polaris/tree/sakubo">Source Code on Github</a>'
    channel = '\nChannel: @PolarisChannel'
    
    about = header + '\n' + license + source + '\n' + channel + '\n' + help

    send_message(m, about, markup='HTML', preview=False)
