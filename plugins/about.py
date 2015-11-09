from __main__ import *
from utilies import *

commands = [
	'^about',
	'^system',
	'^start',
	'/start'
]
description = 'Info about *' + bot.first_name + '*'
typing = True

def action(msg):			
	header = 'Hi! I\'m *#BOT_FIRSTNAME*'
	header += '\nNice to meet you.'

	help = '\nUse ' + config['command_start'] + 'help for a list of commands.'
	license = '\n*#BOT_NAME* is licensed under the *GPLv2*.'	
	source = '\n[Source Code on Github](https://github.com/luksireiku/polaris)'
	channel = '\nChannel: @PolarisUpdates'
	group = '\nJoin [Society of Polaris](https://telegram.me/joinchat/B09roADwf_-EFMjy_9Q1qA)!'
		
	if re.compile(config['command_start'] + 'about').search(msg.text):
		about = header + '\n' + license + channel + group
		about = tag_replace(about, msg)
	
		core.send_message(msg.chat.id, about, disable_web_page_preview=True, parse_mode="Markdown")
		
	elif re.compile(config['command_start'] + 'system').search(msg.text):
		running = '\n*Running on*:\n'
		running += '\t*System*: ' + subprocess.check_output('head -n1 /etc/issue | cut -d " " -f -3', shell=True)
		running += '\t*Kernel*: ' + subprocess.check_output('uname -rs', shell=True)
		running += '\t*Processor*: ' + subprocess.check_output('cat /proc/cpuinfo | grep "model name" | tr -s " " | cut -d " " -f 3-', shell=True)
		running += '\t*RAM*: ' + subprocess.check_output('dmidecode | grep "Range Size" | head -n 1 | cut -d " " -f 3-', shell=True)
		running += '\t*Python*: ' + str(platform.python_version()) + ' (' + str(platform.python_compiler()) + ')' + '\n'
		running += '\t*Uptime*: ' + subprocess.check_output('uptime -p', shell=True)
		
		core.send_message(msg.chat.id, running, parse_mode="Markdown")
		
	else:
		start = tag_replace(header, msg)
		
		core.send_message(msg.chat.id, start, parse_mode="Markdown")