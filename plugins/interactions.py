# -*- coding: utf-8 -*-
from __main__ import *
from utilies import *


commands = [
    ''
]

hidden = True


def run(msg):
    input = msg['text'].lower()

    for interaction in locale[get_locale(msg['chat']['id'])]['interactions']:
        for trigger in locale[get_locale(msg['chat']['id'])]['interactions'][interaction]:
            trigger = tag_replace(trigger, msg)
            if re.match(trigger.lower(), input):
                interaction = tag_replace(interaction, msg)
                return send_message(msg['chat']['id'], interaction, parse_mode="Markdown")
