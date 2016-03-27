from core.utils import *
from core.bot import start

commands = [
    ('/sh', ['command']),
    ('/msg', ['chat id', 'message']),
    ('/reload', []),
    ('/refreshplugins', []),
    ('/shutdown', [])
]

hidden = True


def run(m):
    if not is_admin(m.sender.id):
        return send_message(m, lang.errors.permission)

    input = get_input(m)

    if get_command(m) == 'sh':
        if not input:
            return send_message(m, lang.errors.argument)
        message = '<code>%s</code>' % (subprocess.getoutput(input))

    elif get_command(m) == 'msg':
        if not input:
            return send_message(m, lang.errors.argument)
        chat_id = first_word(input)
        text = get_input(input)

        if not send_message(chat_id, text):
            return send_message(m, lang.errors.argument)
        return

    elif get_command(m) == 'reload':
        message = '%s reloading!' % bot.first_name
        send_message(m, message, markup='HTML')
        start()

    elif get_command(m) == 'refreshplugins':
        message = 'Refreshing  %s plugin...' % bot.first_name
        send_message(m, message, markup='HTML')

        bot.list_plugins()
        config.save(config)

    elif get_command(m) == 'shutdown':
        bot.started = False
        message = '%s shutdown!' % bot.first_name

    send_message(m, message, markup='HTML')
