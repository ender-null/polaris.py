# -*- coding: utf-8 -*-
from utilies import *
import random


commands = ['^rae']

parameters = {('word', True)}
description = 'Search that word in Spanish dictionary.'
action = 'typing'
hidden = True


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")

    url = 'http://dulcinea.herokuapp.com/api/'
    params = {'query': input}

    jdat = send_request(url, params=params)

    if not jdat:
        return send_error(msg, 'connection')

    if jdat['status'] == 'error':
        return send_error(msg, 'unknown')

    while jdat['type'] == 'multiple':
        params = {'query': jdat['response'][0]['id']}
        jdat = send_request(url, params=params)
    
    responses = len(jdat['response'])
    
    if responses == 0:
        return send_error(msg, 'results')
        
    if responses > 5:
        responses = 5

    text = ''    
    for i in range(0, responses):
        text += '\n\n*' + jdat['response'][i]['word'] + '*'
        meanings = len(jdat['response'][i]['meanings'])
        if meanings > 5:
            meanings = 5
        
        for m in range(0, meanings):
            text += '\n\t*' + str(m+1) + '.* ' + jdat['response'][i]['meanings'][m]['meaning']

    send_message(msg['chat']['id'], text, parse_mode="Markdown")
