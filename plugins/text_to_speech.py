from __main__ import *
from utilies import *
from gtts import gTTS

doc = config.command_start + 'tts *[text]*\nGenerates an audio file using Google Text-To-Speech API.'

triggers = {
	'^' + config.command_start + 'tts',
	'^' + config.command_start + 'voice',
	'^' + config.command_start + 'v ',
	'^' + config.command_start + 'say',
}

def action(msg):			
	input = get_input(msg.text)
	
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")
	
	if first_word(input)=='es':
		lang = 'es'
		text = all_but_first_word(input)
	else:
		lang = 'en'
		text = input
	
	tmp = 'tmp/'
	name = os.path.splitext(str(time.mktime(datetime.datetime.now().timetuple())))[0]
	filename = name + '.mp3'
	open_temporal(tmp)
	
	try:
		tts = gTTS(text=text, lang=lang)
	except Exception as e:
		core.send_message(msg.chat.id, str(e))
		
	tts.save(tmp + filename)
	
	filename = convert_to_voice(tmp, filename)
	
	file = open(tmp + filename, 'rb')
	
	core.send_chat_action(chat, 'upload_audio')
	core.send_audio(chat, file)
	
	clean_temporal(tmp, filename)