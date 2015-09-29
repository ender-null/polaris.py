import __main__
import utilies
import sys
import datetime
import platform
import subprocess
import re

doc = '/about\nInfo about *' + __main__.bot.first_name + '*'
triggers = {
	'^/about',
	'^/start',
	'^/system'
}

def action(msg):			
	header = 'Hello #FROM_FIRSTNAME!'
	header += '\nMy name is *#BOT_FIRSTNAME*, nice to meet you.'
	header += '\nI\'m a multi-purpose Telegram Bot developed by @luksireiku.'

	help = '\nUse /help for a list of commands.'
	license = '\n@#BOT_USERNAME is licensed under the *GPLv2*.'	
	source = '\n[Source Code on Github](https://github.com/luksireiku/polaris)'
	
	running = '\n*Running on*:\n'
	running += '*System*: ' + subprocess.check_output('head -n1 /etc/issue | cut -d " " -f -3', shell=True)
	running += '*Kernel*: ' + subprocess.check_output('uname -rs', shell=True)
	running += '*Processor*: ' + subprocess.check_output('cat /proc/cpuinfo | grep "model name" | tr -s " " | cut -d " " -f 3-', shell=True)
	running += '*RAM*: ' + subprocess.check_output('dmidecode | grep "Range Size" | head -n 1 | cut -d " " -f 3-', shell=True)
	running += '*Python*: ' + str(platform.python_version()) + ' (' + str(platform.python_compiler()) + ')' + '\n'
	running += '*Uptime*: ' + subprocess.check_output('uptime -p', shell=True)
	
	text = header + '\n' + license + '\n' + help
	text = utilies.tag_replace(text, msg)
	
	if re.compile('/system').search(msg.text):
		__main__.tb.send_message(msg.chat.id, running, disable_web_page_preview=True, parse_mode="Markdown")
	else:
		__main__.tb.send_message(msg.chat.id, text, disable_web_page_preview=True, parse_mode="Markdown")

plugin = {
    'doc': doc,
    'triggers': triggers,
    'action': action,
	'typing': None
}