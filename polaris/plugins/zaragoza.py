from polaris.utils import get_input, get_coords, send_request, download, remove_html


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            "/bus": {
                'friendly': "^Bus ",
                'parameters': {
                    "número de parada": True
                },
            },
            "/tranvia": {
                'friendly': "^Tranvia ",
                'parameters': {
                    "número de parada": True
                },
            },
            "/bizi": {
                'friendly': "^Bizi ",
                'parameters': {
                    "número de estación": True
                },
            },
        }
        self.description = "Servicio pensado para reutilizadores que pone a su disposición información sobre las operaciones que puede realizar sobre unos determinados conjuntos de datos de Zaragoza."

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        baseurl = 'http://www.zaragoza.es/api'

        if '/bus' in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

            url = baseurl + '/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-' + input.lstrip(
                '0') + '.json'
            params = {
                'srsname': 'wgs84'
            }

            data = send_request(url, params=params)
            if 'error' in data:
                return self.bot.send_message(m, self.bot.lang.errors.no_results, extra={'format': 'HTML'})

            street = data['title'].split(')')[-1].split('Lí')[0].strip().title()
            parada = data['title'].split(')')[0].replace('(', '')
            line = data['title'].title().split(street)[-1].strip().replace('Líneas: ','')
            buses = []

            text = '<b>%s</b>\n\tParada: <b>%s</b>  [%s]\n\n' % (street, parada, line)

            for destino in data['destinos']:
                try:
                    tiempo = int(destino['primero'].replace(' minutos', '').rstrip('.'))
                except Exception as e:
                    print(e)
                    tiempo = destino['primero'].rstrip('.').replace('cin', 'ción')

                buses.append((
                    destino['linea'],
                    destino['destino'].rstrip(',').rstrip('.').title(),
                    tiempo
                ))

                try:
                    tiempo = int(destino['segundo'].replace(' minutos', '').rstrip('.'))
                except Exception as e:
                    print(e)
                    tiempo = destino['segundo'].rstrip('.').replace('cin', 'ción')

                buses.append((
                    destino['linea'],
                    destino['destino'].rstrip(',').rstrip('.').title(),
                    tiempo
                ))
            
            try:
                buses = sorted(buses, key=lambda bus: bus[2])
            except:
                pass

            for bus in buses:
                text += ' • <b>%s min.</b>  %s <i>%s</i>\n' % (bus[2], bus[0], bus[1])

            text = text.rstrip('\n')
            
            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        elif '/tranvia' in m.content:
            if not input:
                return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

            url = baseurl + '/recurso/urbanismo-infraestructuras/tranvia/' + input.lstrip('0') + '.json'
            params = {
                'rf': 'html',
                'srsname': 'wgs84'
            }

            data = send_request(url, params=params)
            if 'status' in data:
                return self.bot.send_message(m, self.bot.lang.errors.no_results, extra={'format': 'HTML'})

            tranvias = []

            text = '<b>%s</b>\n\tParada: <b>%s</b>\n\n' % (data['title'].title(), data['id'])

            for destino in data['destinos']:
                tranvias.append((
                    destino['linea'],
                    destino['destino'].rstrip(',').rstrip('.').title(),
                    int(destino['minutos'])
                ))
            
            try:
                tranvias = sorted(tranvias, key=lambda tranvia: tranvia[2])
            except:
                pass

            for tranvia in tranvias:
                text += ' • <b>%s min.</b>  %s <i>%s</i>\n' % (tranvia[2], tranvia[0], tranvia[1])

            text += '\n%s' % data['mensajes'][-1].replace('INFORMACIN','INFORMACIÓN').capitalize()

            text = text.rstrip('\n')
            
            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        elif '/bizi' in m.content:
            if input:
                start = input
            else:
                start = 0

            url = baseurl + '/recurso/urbanismo-infraestructuras/estacion-bicicleta/' + input.lstrip('0') + '.json'
            params = {
                'rf': 'html',
                'srsname': 'utm30n'
            }

            data = send_request(url, params=params)
            if 'error' in data:
                return self.bot.send_message(m, self.bot.lang.errors.no_results, extra={'format': 'HTML'})

            text = '<b>%s</b>\n\tEstación: <b>%s</b>\n\n<b>Bicicletas disponibles:</b> <i>%s</i> de <i>%s</i>\n<b>Actualizado</b>: %s' % (data['title'].title(), data['id'], data['bicisDisponibles'], data['anclajesDisponibles'], data['lastUpdated'])
            
            return self.bot.send_message(m, text, extra={'format': 'HTML'})
