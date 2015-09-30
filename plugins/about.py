from __main__ import *
from utilies import *

doc = config.command_start + 'about\nInfo about *' + bot.first_name + '*'
triggers = {
	'^' + config.command_start + 'about',
	'^' + config.command_start + 'system',
	'^' + config.command_start + 'start',
	'^/start',
}

def action(msg):			
	header = 'Hi! I\'m *#BOT_FIRSTNAME*'
	header += '\nNice to meet you.'

	help = '\nUse ' + config.command_start + 'help for a list of commands.'
	license = '\n*#BOT_NAME* is licensed under the *GPLv2*.'	
	source = '\n[Source Code on Github](https://github.com/luksireiku/polaris)'
	channel = '\nChannel: @PolarisUpdates'
		
	about = header + '\n' + source + license + channel
	about = utilies.tag_replace(about, msg)
	start = utilies.tag_replace(header, msg)
	
	running = '\n*Running on*:\n'
	running += '*System*: ' + subprocess.check_output('head -n1 /etc/issue | cut -d " " -f -3', shell=True)
	running += '*Kernel*: ' + subprocess.check_output('uname -rs', shell=True)
	running += '*Processor*: ' + subprocess.check_output('cat /proc/cpuinfo | grep "model name" | tr -s " " | cut -d " " -f 3-', shell=True)
	running += '*RAM*: ' + subprocess.check_output('dmidecode | grep "Range Size" | head -n 1 | cut -d " " -f 3-', shell=True)
	running += '*Python*: ' + str(platform.python_version()) + ' (' + str(platform.python_compiler()) + ')' + '\n'
	running += '*Uptime*: ' + subprocess.check_output('uptime -p', shell=True)
		
	if re.compile(config.command_start + 'about').search(msg.text):
		core.send_message(msg.chat.id, about, disable_web_page_preview=True, parse_mode="Markdown")
	elif re.compile(config.command_start + 'system').search(msg.text):
		core.send_message(msg.chat.id, running, parse_mode="Markdown")
	else:
		core.send_message(msg.chat.id, start, disable_web_page_preview=True, parse_mode="Markdown")

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}