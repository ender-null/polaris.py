from __main__ import *
from utilies import *

commands = [
	''
]
hidden = True

def action(msg):
	input = msg.text.lower()

	for interaction in locale[get_locale(msg.chat.id)]['interactions']:
		for trigger in locale[get_locale(msg.chat.id)]['interactions'][interaction]:
			trigger = tag_replace(trigger, msg)
			if re.compile(trigger.lower()).search(input):
				interaction = tag_replace(interaction, msg)
				core.send_chat_action(msg.chat.id, 'typing')
				return core.send_message(msg.chat.id, interaction, parse_mode="Markdown")