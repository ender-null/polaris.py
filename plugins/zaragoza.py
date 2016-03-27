from core.utils import *

commands = [
    ('/poste', ['numero']),
    ('/bus', ['linea'])
]
description = 'Servicio pensado para reutilizadores que pone a su disposición información sobre las operaciones que puede realizar sobre unos determinados conjuntos de datos de Zaragoza.'
hidden = True


def run(m):
    input = get_input(m)

    if not input:
        return send_message(m, lang.errors.input)
    
    if get_command(m) == 'poste':
        url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-' + input.lstrip(
            '0') + '.json'
        params = {
            'srsname': 'wgs84'
        }
        jstr = requests.get(url, params=params, timeout=config.timeout)

        if jstr.status_code != 200:
            send_alert('%s\n%s' % (lang.errors.connection, jstr.text))
            return send_message(m, lang.errors.connection)

        jdat = json.loads(jstr.text)

        street = jdat['title'].split(')')[-1].split('Lí')[0].strip()
        poste = jdat['title'].split(')')[0]
        line = jdat['title'].split(street)[-1].strip()

        text = '<b>{0}</b>\n\tPoste: {1}\n\t{2}\n\n'.format(street.title(), poste, line)
        for destino in jdat['destinos']:
            text += destino['linea'] + ' ' + destino['destino']
            text += '\n - ' + destino['primero']
            text += '\n - ' + destino['segundo']
            text += '\n'
        text = text.rstrip('\n')
        
        send_message(m, text, markup='HTML')
    
    elif get_command(m) == 'bus':
        url = 'https://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/linea/' + input + '.json'
        params = {
            'srsname': 'wgs84'
        }
        jstr = requests.get(url, params=params, timeout=config.timeout)

        if jstr.status_code != 200:
            send_alert('%s\n%s' % (lang.errors.connection, jstr.text))
            return send_message(m, lang.errors.connection)

        jdat = json.loads(jstr.text)
        
        markers = []
        max = 30
        for item in jdat['result']:
            if item['geometry']['type'] == 'Point':
                lat = item['geometry']['coordinates'][1].__round__(6)
                lon = item['geometry']['coordinates'][0].__round__(6)
                markers.append('color:red|label:%s|%s,%s' % ('p', lat, lon))
                max -= 1
                
                if max == 0:
                    break

        map_url = 'https://maps.googleapis.com/maps/api/staticmap'
        map_params = {
            'key': config.keys.google_developer_console,
            'size': '640x320',
            'markers': markers
        }
                
        map = download(map_url, map_params, method = 'post')

        if map:
            send_photo(m, map)
        else:
            send_message(m, lang.errors.download)
