# -*- coding: utf-8 -*-
from utils import *

commands = [
    '^remindme',
    '^reminder',
    '^remind$',
    '^r '
]

parameters = (
    ('delay', True),
    ('message', True),
)

description = 'Set a reminder for yourself. First argument is delay until you wish to be reminded.\nExample: `' + config['command_start'] + 'remindme 2h GiT GuD`'
action = 'typing'
hidden = True

reminders = load_json('data/reminders.json')

def to_seconds(time, unit):
    if unit == 's':
        return float(time)
    elif unit == 'm':
        return float(time) * 60
    elif unit == 'h':
        return float(time) * 60 * 60
    elif unit == 'd':
        return float(time) * 60 * 60 * 24

def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc,
                            parse_mode="Markdown")
    delay = first_word(input)
    if delay:
        time = delay[:-1]
        unit = delay[-1:]
        if not is_int(time) or is_int(unit):
            message = 'The delay must be in this format: `(integer)(s|m|h|d)`.\nExample: `2h` for 2 hours.'
            return send_message(msg['chat']['id'], message, parse_mode="Markdown")
    try:
        alarm = now() + to_seconds(time, unit)
    except:
        return send_message(msg['chat']['id'], message, parse_mode="Markdown")
        
    text = all_but_first_word(input)
    if not text:
        send_message(msg['chat']['id'], 'Please include a reminder.')
        
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
    send_message(msg['chat']['id'], message, parse_mode="Markdown")

def cron():
    reminders = load_json('data/reminders.json', True)
    for id, reminder in reminders.items():
        if now() > reminder['alarm']:
            send_message(reminder['chat_id'], reminder['text'])
            del reminders[id]
            save_json('data/reminders.json', reminders)
