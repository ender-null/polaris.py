from polaris.utils import get_input, get_coords, send_request, download, remove_html


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            "/poste": {
                'friendly': "^Poste ",
                'parameters': {
                    "número de parada": True
                },
            }
        }
        self.description = "Servicio pensado para reutilizadores que pone a su disposición información sobre las operaciones que puede realizar sobre unos determinados conjuntos de datos de Zaragoza."

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        if not input:
            return self.bot.send_message(m, self.bot.lang.errors.missing_parameter, extra={'format': 'HTML'})

        url = 'http://www.zaragoza.es/api/recurso/urbanismo-infraestructuras/transporte-urbano/poste/tuzsa-' + input.lstrip(
            '0') + '.json'
        params = {
            'srsname': 'wgs84'
        }

        data = send_request(url, params=params)

        street = data['title'].split(')')[-1].split('Lí')[0].strip()
        poste = data['title'].split(')')[0].replace('(', '')
        line = data['title'].split(street)[-1].strip()

        text = '<b>{0}</b>\n\tPoste: {1}\n\t{2}\n\n'.format(street.title(), poste, line)
        for destino in data['destinos']:
            text += '<b>%s %s</b>' % (destino['linea'], destino['destino'].rstrip(',').rstrip('.').title())
            text += '\n • ' + destino['primero'].rstrip('.').replace('cin', 'ción')
            text += '\n • ' + destino['segundo'].rstrip('.').replace('cin', 'ción')
            text += '\n\n'
        text = text.rstrip('\n')
        
        return self.bot.send_message(m, text, extra={'format': 'HTML'})
