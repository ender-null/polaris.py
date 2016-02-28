from core.utils import *

commands = [
    ('/getdata', [])
]
description = 'Testing plugin.'


def run(m):
    send_message(m, show_message(m), markup ='Markdown', preview = False)
