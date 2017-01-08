from chatterbot import ChatBot


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '^@%s' % self.bot.info.username,
                'parameters': [],
                'hidden': True
            },
            {
                'command': '^%s' % self.bot.info.first_name.split()[0],
                'parameters': [],
                'hidden': True
            }
        ]
        self.chatter = ChatBot(
            self.bot.info.first_name,
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
            storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
            database='chatter-database-%s' % self.bot.config.translation
        )
        if self.bot.config.translation != 'default':
            self.chatter.train("chatterbot.corpus.spanish")
        else:
            self.chatter.train("chatterbot.corpus.english")


    # Plugin action #
    def run(self, m):
        input = m.content.replace('@%s ' % self.bot.info.username, '')

        if m.type != 'text':
            input = '%s:%s' % (m.type, input)

        try:
            text = self.chatter.get_response(input)
        except Exception as e:
            self.bot.send_alert(traceback.format_exc())
            text = '😕'

        text = str(text)
        text = text.replace('@%s ' % self.bot.info.username, '')

        if ':' in text and text.split(':')[0] != '':
            type = text.split(':')[0]
            content = ''.join(text.split(':')[1:])
            return self.bot.send_message(m, content, type)

        else:
            text = text.capitalize()
            return self.bot.send_message(m, text)


    def always(self, m):
        # The bot will talk if you PM it and don't use any command. #
        if (m.conversation.id > 0 and
            not m.content.startswith(self.bot.config.prefix) and
            not m.content.startswith('/start') and
            not m.content.startswith('/help')):
            m.content = '@%s %s' % (self.bot.info.username, m.content)


        # The bot will talk if you reply to it's messages, ignoring commands. #
        if (m.reply and
            m.reply.sender.id == self.bot.info.id and
            not m.content.startswith(self.bot.config.prefix)):
            m.content = '@%s %s' % (self.bot.info.username, m.content)
