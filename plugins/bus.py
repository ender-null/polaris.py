# -*- coding: utf-8 -*-
from utils import *


commands = [
    '^bus',
    '^b ',
    '^poste',
    '^zgzbus',
]

parameters = (
    ('poste', True),
)

description = 'Gets real time bus poste data. Only works for [Urbanos de Zaragoza](http://www.urbanosdezaragoza.es).'
action = 'typing'
hidden = True


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")
    
    url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-' + input.lstrip('0') + '.json'

    jdat = send_request(url)

    if not jdat:
        return send_error(msg, 'connection')

    if 'error' in jdat:
        return send_error(msg, 'unknown')

    #text = jdat['title'] + '\n'
    text = ''
    for destino in jdat['destinos']:
        text += destino['linea'] + ' ' + destino['destino']
        text += '\n\t\t\t\t' + destino['primero']
        text += '\n\t\t\t\t' + destino['segundo']
        text += '\n'

    lon, lat = jdat['geometry']['coordinates']
    lat = float(lat) / 1000000
    lon = float(lon) / 1000000
    
    photo_url = 'https://maps.googleapis.com/maps/api/streetview'
    photo_params = {
        'size': '640x320',
        'location': str(lat) + ',' + str(lon),
        'pitch': 16,
        'key': config['api']['googledev']
    }
    jstr = requests.get(photo_url, params=photo_params)
    
    photo = download(photo_url, params=photo_params)
    #send_photo(msg['chat']['id'], photo, caption=text):

    send_message(msg['chat']['id'], text, parse_mode="Markdown")
