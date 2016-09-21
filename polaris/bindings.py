from polaris.types import Message

def send_message(bot, msg, text, reply=None, markup=None):
    message = Message(None, msg.conversation, bot.info, text, 'text', reply=reply, markup=markup)
    bot.outbox.put(message)

