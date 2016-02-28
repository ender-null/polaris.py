from core.utils import *

commands = [
    ('/poste', ['numero'])
]
description = 'Servicio pensado para reutilizadores que pone a su disposición información sobre las operaciones que puede realizar sobre unos determinados conjuntos de datos de Zaragoza.'
hidden = True


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, 'No input')

    url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-' + input.lstrip(
        '0') + '.json'
    params = {
        'srsname': 'wgs84'
    }
    jstr = requests.get(url, params=params)

    if jstr.status_code != 200:
        return send_message(m, 'Connection Error!\n' + jstr.text)

    jdat = json.loads(jstr.text)

    text = '*{}*\n'.format(jdat['title'])
    for destino in jdat['destinos']:
        text += destino['linea'] + ' ' + destino['destino']
        text += '\n - ' + destino['primero']
        text += '\n - ' + destino['segundo']
        text += '\n'
    text = text.rstrip('\n')

    send_message(m, text)
