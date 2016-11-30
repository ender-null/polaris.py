from chatterbot import ChatBot


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = [
            {
                'command': '@%s' % self.bot.info.username,
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
            storage_adapter="chatterbot.adapters.storage.JsonFileStorageAdapter",
            database='polaris/data/%s.chatter.json' % self.bot.name,
            logic_adapters=[
                "chatterbot.adapters.logic.MathematicalEvaluation",
                "chatterbot.adapters.logic.TimeLogicAdapter",
                "chatterbot.adapters.logic.ClosestMatchAdapter"
            ],
            filters=["chatterbot.filters.RepetitiveResponseFilter"]
        )
        if self.bot.config.translation != 'default':
            self.chatter.train("chatterbot.corpus.spanish")
        else:
            self.chatter.train("chatterbot.corpus.english")


    # Plugin action #
    def run(self, m):
        try:
            text = str(self.chatter.get_response(m.content))
        except Exception as e:
            text = '😕'

        text = text.replace('@%s' % self.bot.info.username, '').capitalize()

        if text:
            return self.bot.send_message(m, text)
        else:
            return self.bot.send_message(m, self.bot.trans.errors.connection_error)


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
