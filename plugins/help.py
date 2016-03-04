from core.utils import *

commands = [
    ('/help', ['command'])
]
description = 'Prints help.'


def run(m):
    input = get_input(m)

    message = lang.errors.results

    if input:
        for plugin in plugins:
            for command, parameters in plugin.commands:
                if command.replace('/', '') == input:
                    message = plugin.description + '\n\n'
                    message += '\t' + command.replace("/", config.start)
                    for parameter in parameters:
                        message += ' *<' + parameter + '>*'
    else:
        message = '*Commands*:\n'
        for plugin in plugins:
            if hasattr(plugin, 'hidden') and plugin.hidden:
                continue
            for command, parameters in plugin.commands:
                message += '\t' + command.replace('/', config.start)
                for parameter in parameters:
                    message += ' *<' + parameter + '>*'
                message += '\n'

    send_message(m, message, markup='Markdown')
