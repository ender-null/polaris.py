from core.utils import *

commands = [
    ('/remindme', ['delay', 'message'])
]
description = 'Set a reminder for yourself. First argument is delay until you wish to be reminded.\nExample: "' + config.start + 'remindme 2h GiT GuD"'

reminders = load_json('data/reminders.json', True)

def to_seconds(time, unit):
    if unit == 's':
        return float(time)
    elif unit == 'm':
        return float(time) * 60
    elif unit == 'h':
        return float(time) * 60 * 60
    elif unit == 'd':
        return float(time) * 60 * 60 * 24


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    delay = first_word(input)
    if delay:
        time = delay[:-1]
        unit = delay[-1:]
        if not is_int(time) or is_int(unit):
            message = 'The delay must be in this format: "(integer)(s|m|h|d)".\nExample: "2h" for 2 hours.'
            return send_message(m, message)
    try:
        alarm = now() + to_seconds(time, unit)
    except:
        return send_message(msg['chat']['id'], message, parse_mode="Markdown")

    text = all_but_first_word(input)
    if not text:
        send_message(m, 'Please include a reminder.')

    if 'username' in msg['from']:
        text += '\n@' + msg['from']['username']

    reminder = OrderedDict()
    reminder['alarm'] = alarm
    reminder['chat_id'] = msg['chat']['id']
    reminder['text'] = text

    reminders[int(now())] = reminder
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
        if now() > reminder['alarm']:
            # send_message(reminder['chat_id'], reminder['text'])
            send_message(m, reminder['text'], markup='Markdown')
            del reminders[id]
            save_json('data/reminders.json', reminders)
