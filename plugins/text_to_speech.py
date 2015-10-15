from __main__ import *
from utilies import *
from gtts import gTTS

doc = config['command_start'] + 'speech *[text]*\nGenerates an audio file using Google Text-To-Speech API.'

triggers = {
	'^' + config['command_start'] + 'tts',
	'^' + config['command_start'] + 'speech',
}

langs = [
	'af', 'aq', 'ar', 'hy', 'ca', 'zh', 'zh-cn', 'zh-tw', 'zh-yue',
	'hr', 'cs', 'da', 'nl', 'en-au', 'en-uk', 'en-us', 'eo',
	'fi', 'fr', 'de', 'el', 'ht', 'hu', 'is', 'id',
	'it', 'ja', 'ko', 'la', 'lv', 'mk', 'no', 'pl',
	'pt', 'pt-br', 'ro', 'ru', 'sr', 'sk', 'es', 'es-es',
	'es-us', 'sw', 'sv', 'ta', 'th', 'tr', 'vi', 'cy'
]

def action(msg):			
	input = get_input(msg.text)
	
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	for v in langs:
		if first_word(input) == v:
			lang = v
			text = all_but_first_word(input)
			break
		else:
			lang = 'en'
			text = input
		
	tmp = 'tmp/'
	name = os.path.splitext(str(time.mktime(datetime.datetime.now().timetuple())))[0]
	filename = name + '.mp3'
	open_temporal(tmp)
	
	tts = gTTS(text=text, lang=lang)
	tts.save(tmp + filename)
	
	filename = convert_to_voice(tmp, filename)
	
	file = open(tmp + filename, 'rb')
	
	core.send_chat_action(chat, 'upload_audio')
	core.send_audio(chat, file)
	
	clean_temporal(tmp, filename)