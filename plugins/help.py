from core.utils import *

commands = [
    ('/help', ['command'])
]
description = 'Prints help.'
shortcut = '/h '


def run(m):
    input = get_input(m)

    message = lang.errors.results

    if input:
        for plugin in plugins:
            for command, parameters in plugin.commands:
                if command.replace('/', '') == input:
                    message = plugin.description + '\n'
                    for command, parameters in plugin.commands:
                        message += '\n\t' + command.replace('/', config.start)
                        if hasattr(plugin, 'shortcut'):
                            message += ' | %s' % plugin.shortcut.replace('/', config.start)
                    
                        for parameter in parameters:
                            message += ' <b>&lt;' + parameter + '&gt;</b>'
                    break
    else:
        message = '<b>Commands</b>:\n'
        for plugin in plugins:
            if hasattr(plugin, 'hidden') and plugin.hidden:
                continue
            for command, parameters in plugin.commands:
                message += '\t%s' % command.replace('/', config.start)
                if hasattr(plugin, 'shortcut'):
                    message += ' | %s' % plugin.shortcut.replace('/', config.start)
                
                for parameter in parameters:
                    message += ' <b>&lt;' + parameter + '&gt;</b>'
                message += '\n'

    send_message(m, message, markup='HTML')
