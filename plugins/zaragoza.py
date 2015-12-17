# -*- coding: utf-8 -*-
from utils import *


commands = [
    '^bus',
    '^tranvia',
    '^poste'
]

parameters = (
    ('id', True),
)

description = 'Servicio pensado para reutilizadores que pone a su disposición información sobre las operaciones que puede realizar sobre unos determinados conjuntos de datos de Zaragoza.'
action = 'typing'
hidden = True


def run(msg):
    input = get_input(msg['text'])

    if not input:
        doc = get_doc(commands, parameters, description)
        return send_message(msg['chat']['id'], doc, parse_mode="Markdown")
    if (get_command(msg['text']) == 'bus' or
        get_command(msg['text']) == 'poste'):
        url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-' + input.lstrip('0') + '.json'
        params = {
            'srsname': 'wgs84'
        }
        jdat = send_request(url, params)

        if not jdat:
            return send_error(msg, 'connection')

        if 'error' in jdat:
            return send_error(msg, 'unknown')

        title = '*{}*\n'.format(jdat['title'])
        text = ''
        for destino in jdat['destinos']:
            text += destino['linea'] + ' ' + destino['destino']
            text += '\n - ' + destino['primero']
            text += '\n - ' + destino['segundo']
            text += '\n'
        text = text.rstrip('\n')
        lon, lat = jdat['geometry']['coordinates']

        photo_url = 'https://maps.googleapis.com/maps/api/streetview'
        photo_params = {
            'size': '640x320',
            'location': str(lat) + ',' + str(lon),
            'pitch': 16,
            'key': config['api']['googledev']
        }

        photo = download(photo_url, params=photo_params)
        if not send_photo(msg['chat']['id'], photo, text, reply_to_message_id=msg['message_id']):
            send_message(msg['chat']['id'], title + text, reply_to_message_id=msg['message_id'], parse_mode="Markdown")

    elif get_command(msg) == 'tranvia':
        pass
