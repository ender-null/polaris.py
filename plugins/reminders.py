from core.utils import *
from time import time

commands = [
    ('/remindme', ['delay', 'message'])
]
description = 'Set a reminder for yourself. First argument is delay until you wish to be reminded.\nExample: "' + config.start + 'remindme 2h GiT GuD"'

reminders = load_json('data/reminders.json', True)

def to_seconds(delaytime, unit):
    if unit == 's':
        return float(delaytime)
    elif unit == 'm':
        return float(delaytime) * 60
    elif unit == 'h':
        return float(delaytime) * 60 * 60
    elif unit == 'd':
        return float(delaytime) * 60 * 60 * 24


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)

    delay = first_word(input)
    if delay:
        delaytime = delay[:-1]
        unit = delay[-1:]
        if not is_int(delaytime) or is_int(unit):
            message = 'The delay must be in this format: "(integer)(s|m|h|d)".\nExample: "2h" for 2 hours.'
            return send_message(m, message)

    alarm = time() + to_seconds(delaytime, unit)

    text = all_but_first_word(input)
    if not text:
        send_message(m, 'Please include a reminder.')

    reminder = DictObject(OrderedDict())
    reminder.alarm = alarm
    reminder.chat_id = m.receiver.id
    reminder.text = text
    reminder.first_name = m.sender.first_name
    reminder.username = m.sender.username

    reminders[str(time())] = reminder
    save_json('data/reminders.json', reminders)

    if unit == 's':
        delay = delay.replace('s', ' seconds')
    if unit == 'm':
        delay = delay.replace('m', ' minutes')
    if unit == 'h':
        delay = delay.replace('h', ' hours')
    if unit == 'd':
        delay = delay.replace('d', ' days')

    message = '<b>%s</b>, I\'ll remind you in <b>%s</b> to <i>%s</i>.' % (m.sender.first_name, delay, latcyr(text))
    send_message(m, message, markup='HTML')


def cron():
    for id, reminder in reminders.items():
        if time() > reminder['alarm']:
            text = latcyr('<i>%s</i>\n - %s' % (reminder['text'], reminder['first_name']))
            if reminder['username']:
                text += ' (@%s)' % reminder['username']

            m = Message()
            if reminder['chat_id'] > 0:
                m.sender = User()
                m.sender.id = reminder['chat_id']
                m.receiver = User()
                m.receiver.id = bot.id
            else:
                m.receiver = Group()
                m.receiver.id = reminder['chat_id']

            send_message(m, text, markup='HTML')
            del reminders[id]
            save_json('data/reminders.json', reminders)
