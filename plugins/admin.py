from core.utils import *
from core import bot

commands = {
    '/run': {},
    '/msg': {},
    '/reload': {},
    '/refreshplugins': {},
    '/shutdown': {}
}

def run(m):
    if not is_admin(m.sender.id):
        return send_msg(m, 'No, shit isn\'t going that way.')

    input = get_input(m)

    if get_command(m) == 'run':
        if not input:
            return send_msg(m, 'Invalid argument.')
        message = '`{0}`'.format(subprocess.getoutput(input))

    elif get_command(m) == 'msg':
        if not input:
            return send_msg(m, 'Invalid argument.')
        chat_id = first_word(input)
        text = get_input(input)

        if not send_msg(chat_id, text):
            return send_msg(m, 'Invalid argument.')
        return

    elif get_command(m) == 'reload':
        bot.start()
        message = 'Bot reloaded!'
    
    elif get_command(m) == 'refreshplugins':
        bot.list_plugins()
        config.save()
        message = 'Bot reloaded!'

    elif get_command(m) == 'shutdown':
        started = False
        message = 'Bot shutdown!'