# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *


commands = [
    '^help',
    '^commands',
    '^genhelp',
    '^h$'
]

parameters = (('command', False))
description = 'Get list of basic information for all commands, or more detailed documentation on a specified command.'
action = 'typing'
hidden = True


def run(msg):
    input = get_input(msg['text'])

    if input:
        for i, v in plugins.items():
            if not hasattr(v, 'hidden'):
                if config['command_start'] + input == v.commands[0].replace('^', '#'):
                    doc = config['command_start'] + v.commands[0].replace('^', '')
                    if hasattr(v, 'parameters'):
                        doc += format_parameters(v.parameters)
                    doc += '\n' + v.description
                    return send_message(msg['chat']['id'], doc,
                                        parse_mode="Markdown")
    else:
        help = ''
        gen = ''
        for i, v in plugins.items():
            if not hasattr(v, 'hidden'):
                help += '\t' + config['command_start']
                help += v.commands[0].replace('^', '')

                if hasattr(v, 'description'):
                        gen += v.commands[0].replace('^', '')
                        gen += ' - ' + v.description
                        gen += '\n'

                if hasattr(v, 'parameters'):
                        help += format_parameters(v.parameters)
                help += '\n'

        message = '*Commands*:\n' + help

        if get_command(msg['text']) == 'genhelp':
            return send_message(msg['chat']['id'], gen, parse_mode="Markdown",
                                disable_web_page_preview=True)

        if msg['from']['id'] != msg['chat']['id']:
            if not send_message(msg['from']['id'], message,
                                parse_mode="Markdown"):
                return send_message(msg['chat']['id'], message,
                                    parse_mode="Markdown")
            return send_message(msg['chat']['id'],
                                'I have sent it in a *private message*.',
                                parse_mode="Markdown")
        else:
            return send_message(msg['chat']['id'], message,
                                parse_mode="Markdown")
