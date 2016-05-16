from core.utils import *

commands = [
    ('/about', [])
]
description = 'Info about <i>%s</i>' % bot.first_name


def run(m):
    license = 'Using <code>sakubo</code> branch of <b>Polaris</b>, licensed under the <b>GPLv2</b>.'
    warranty = '<b>THIS PROGRAM IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND</b>'

    keyboard = {
        'inline_keyboard': [[
            {
                'text': 'Channel',
                'url': 'http://telegram.me/PolarisChannel'   
            },
            {
                'text': 'Developer',
                'url': 'http://telegram.me/luksireiku'
            },
            {
                'text': 'GitHub',
                'url': 'https://github.com/luksireiku/polaris/tree/sakubo'
            }
        ]]
    }
    
    text = '%s\n\n%s' % (license, warranty)

    send_message(m, text, markup='HTML', preview=False, keyboard=keyboard)
