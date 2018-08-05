from polaris.utils import get_input, is_command, send_request, is_int
from bs4 import BeautifulSoup
import requests

class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '/bus',
                'friendly': '^Bus ',
                'description': 'Tiempos de espera en el poste.',
                'parameters': [
                    { "número de parada": True }
                ],
            },
            {
                'command': '/tranvia',
                'friendly': '^Tranvia ',
                'description': 'Datos de una parada de tranvia.',
                'parameters': [
                    { "número de parada": True }
                ],
            },
            {
                'command': '/bizi',
                'friendly': '^Bizi ',
                'description': 'Datos de una estación Bizi.',
                'parameters': [
                    { "número de estación": True }
                ],
            }
        ]
        self.description = "Servicio pensado para reutilizadores que pone a su disposición información sobre las operaciones que puede realizar sobre unos determinados conjuntos de datos de Zaragoza."

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        baseurl = 'http://www.zaragoza.es/api'

        if is_command(self, 1, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            url = 'http://api.drk.cat/zgzpls/bus/stations'
            params = {
                'number': input
            }
            data = send_request(url, params=params)

            if not data or 'errors' in data:
                if data.errors.status == '404 Not Found':
                    return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

            if data.street:
                text = '<b>%s</b>\n   Parada: <b>%s</b>  [%s]\n\n' % (data.street, data.number, data.lines)
            else:
                text = '<b>Parada: %s</b>\n\n' % (data.number)

            for bus in list(data.transports):
                text += ' • <b>%s</b>  %s <i>%s</i>\n' % (bus.time, bus.line, bus.destination)

            text = text.rstrip('\n')

            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        elif is_command(self, 2, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

            url = 'http://api.drk.cat/zgzpls/tram/stations'
            params = {}
            try:
                int(input)
                params.number = input
            except ValueError:
                params.street = input

            data = send_request(url, params=params)

            if not data or 'errors' in data:
                if data.errors.status == '404 Not Found':
                    return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})
                else:
                    return self.bot.send_message(m, self.bot.trans.errors.connection_error, extra={'format': 'HTML'})

            if data.street:
                text = '<b>%s</b>\n   Parada: <b>%s</b>  [%s]\n\n' % (data.street, data.number, data.lines)
            else:
                text = '<b>Parada: %s</b>\n\n' % (data.number)

            for bus in list(data.transports):
                text += ' • <b>%s</b>  %s <i>%s</i>\n' % (bus.time, bus.line, bus.destination)

            text = text.rstrip('\n')

            return self.bot.send_message(m, text, extra={'format': 'HTML'})

        elif is_command(self, 3, m.content):
            if not input:
                return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})
           

            url = baseurl + '/recurso/urbanismo-infraestructuras/estacion-bicicleta/' + input.lstrip('0') + '.json'
            params = {
                'rf': 'html',
                'srsname': 'utm30n'
            }

            data = send_request(url, params=params)
            if 'error' in data:
                return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

            text = '<b>%s</b>\n   Estación: <b>%s</b>\n\n • Bicis Disponibles: <b>%s</b>\n • Anclajes Disponibles: <b>%s</b>' % (data.title.title(), data.id, data.bicisDisponibles, data.anclajesDisponibles)
            
            return self.bot.send_message(m, text, extra={'format': 'HTML'})
