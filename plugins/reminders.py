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
    # try:
    alarm = time() + to_seconds(delaytime, unit)
    # except:
    #     return send_message(m, lang.errors.unknown, markup='Markdown')

    text = all_but_first_word(input)
    if not text:
        send_message(m, 'Please include a reminder.')

    if m.sender.username:
        text += '\n@' + m.sender.username

    reminder = DictObject(OrderedDict())
    reminder.alarm = alarm
    reminder.chat_id = m.receiver.id
    reminder.text = text

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

    message = 'Your reminder has been set for *' + delay + '* from now:\n\n' + text
    send_message(m, message, markup='Markdown')


def cron():
    for id, reminder in reminders.items():
        if time() > reminder['alarm']:
            # send_message(reminder['chat_id'], reminder['text'])
            m = Message()
            if reminder['chat_id'] > 0:
                m.sender = User()
                m.sender.id = reminder['chat_id']
            else:
                m.receiver = Group()
                m.receiver.id = reminder['chat_id']
            send_message(m, reminder['text'], markup='Markdown')
            del reminders[id]
            save_json('data/reminders.json', reminders)
