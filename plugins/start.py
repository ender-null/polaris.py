from core.utils import *

commands = [
    ('/start', [])
]
description = 'Get started with <i>%s</i>' % bot.first_name
hidden = True 

def run(m):
    header = 'A Python bot using plugins! It\'s still in development right now, so you may get crashes and features may not be fully implemented or can suddenly disappear.'
    help = 'Get the list of all available commands with %shelp, and get more info about me with %sabout.' % (config.start, config.start)
    inline = 'I work in inline mode, using <code>@%s &lt;command&gt; &lt;parameters&gt;</code>, e.g. <code>@%s image cat</code>' % (bot.username, bot.username)
    
    text = '%s\n\n%s\n\n%s' % (header, help, inline)

    send_message(m, text, markup='HTML', preview=False)
