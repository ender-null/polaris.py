# -*- coding: utf-8 -*-
interactions = {
	'#GREETING, *#FROM_FIRSTNAME!*': {
		'hello #BOT_NAME',
		'hey #BOT_NAME',
		'hi #BOT_NAME',
	},
	'#GOODBYE, *#FROM_FIRSTNAME!*': {
		'bye #BOT_NAME',
		'later #BOT_NAME',
		'see ya #BOT_NAME',
	},
	'Thank you, *#FROM_FIRSTNAME!*': {
		'thanks,? #BOT_NAME',
		'thank you,? #BOT_NAME',
		'ty,? #BOT_NAME',
		'thx,? #BOT_NAME',
		'tnx,? #BOT_NAME',
		'arigat*,? #BOT_NAME',
	},
	'Welcome back, *#FROM_FIRSTNAME!*': {
		'^i\'m back',
		'^i\'m home',
		'^tadaima',
	},
	'*#FROM_FIRSTNAME*... >.<': {
		'i love you,? #BOT_NAME',
		'marry me,? #BOT_NAME',
		'#BOT_NAME <3',
	},
	'I\'m sorry *#FROM_FIRSTNAME*...': {
		'bad,? #BOT_NAME',
		'fuck you,? #BOT_NAME',
		'you suck,? #BOT_NAME',
		'u suck,? #BOT_NAME',
		'i hate you,? #BOT_NAME',
		'damn,? #BOT_NAME',
		'dammit,? #BOT_NAME',
		'screw you,? #BOT_NAME',
	},
	'How can I help you, *#FROM_FIRSTNAME*?': {
		'^#BOT_NAME$',
	},
	'_Ack_': {
		'syn'
	}
}
greeting = {
	'morning': u'Ohayō gozaimasu',
	'afternoon': u'Konnichi wa',
	'evening': u'Konban wa',
	'night': u'Konban wa',
}

goodbye = {
	'morning': u'Shitsurei shimasu',
	'afternoon': u'Sayōnara',
	'evening': u'Mata ashita',
	#'night': u'Oyasumi nasai',
	'night': u'Sayōnara',
}

errors = {
	'connection': 'Connection error: {}',
	'results': 'No results found.',
	'argument': 'Invalid argument.',
	'syntax': 'Invalid syntax.',
	'permission': 'Permission denied.',
	'id': 'Must be used via reply or by specifying a user\'s ID.',
	'download': 'Download failed.'
}