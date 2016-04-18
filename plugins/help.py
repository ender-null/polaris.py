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
                    i = 0
                    for command, parameters in plugin.commands:
                        message += '\n\t' + command.replace('/', config.start)
                        if hasattr(plugin, 'shortcut'):
                            if type(plugin.shortcut) is list:
                                if plugin.shortcut[i]:
                                    message += ' | %s' % plugin.shortcut[i].replace('/', config.start)
                            else:
                                message += ' | %s' % plugin.shortcut.replace('/', config.start)
                        for parameter in parameters:
                            message += ' <b>&lt;' + parameter + '&gt;</b>'
                    break
    else:
        message = '<b>Commands</b>:\n'
        for plugin in plugins:
            i = 0
            if hasattr(plugin, 'hidden') and plugin.hidden:
                continue
            for command, parameters in plugin.commands:
                message += '\t%s' % command.replace('/', config.start)
                if hasattr(plugin, 'shortcut'):
                    if type(plugin.shortcut) is list:
                        if plugin.shortcut[i]:
                            message += ' | %s' % plugin.shortcut[i].replace('/', config.start)
                    else:
                        message += ' | %s' % plugin.shortcut.replace('/', config.start)
                
                for parameter in parameters:
                    message += ' <b>&lt;' + parameter + '&gt;</b>'
                message += '\n'
                i += 1

    send_message(m, message, markup='HTML')
