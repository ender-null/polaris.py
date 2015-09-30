interactions = {
	'Konnichi wa, *#FROM_FIRSTNAME!*': {
		'hello #BOT_NAME',
		'hey #BOT_NAME',
		'hi #BOT_NAME',
		'^hello$',
		'^hi$',
	},
	'Sayonara, *#FROM_FIRSTNAME!*': {
		'bye #BOT_NAME',
		'later #BOT_NAME',
		'see ya #BOT_NAME'
		'^sayonara$',
		'^oyasumi$',
		'^cya$',
		'^see ya$',
	},
	'Arigato, *#FROM_FIRSTNAME!*': {
		'thanks,? #BOT_NAME',
		'thank you,? #BOT_NAME',
		'ty,? #BOT_NAME',
		'thx,? #BOT_NAME',
		'tnx,? #BOT_NAME',
		'arigat*,? #BOT_NAME',
	},
	'Okaeri nasai, *#FROM_FIRSTNAME!*': {
		'^i\'m back',
		'^i\'m home',
		'^tadaima',
	},
	'*#FROM_FIRSTNAME*...': {
		'i love you,? #BOT_NAME',
		'marry me,? #BOT_NAME',
		'#BOT_NAME <3',
	},
	'Gomen nasai *#FROM_FIRSTNAME*...': {
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
errors = {
	'connection': 'Connection error: {}',
	'results': 'No results found.',
	'argument': 'Invalid argument.',
	'syntax': 'Invalid syntax.',
	'permission': 'Permission denied.',
	'id': 'Must be used via reply or by specifying a user\'s ID.',
	'download': 'Download failed.'
}