from polaris.types import Message, Conversation, User
from polaris.utils import send_request
from six import string_types
import logging


class bindings(object):
    def __init__(self, bot):
        self.bot = bot

    def api_request(self, api_method, params=None, headers=None, files=None):
        url = 'https://api.telegram.org/bot%s/%s' % (self.bot.config.bindings_token, api_method)
        try:
            return send_request(url, params, headers, files, post=True)
        except:
            return None

    def get_me(self):
        r = self.api_request('getMe')
        return User(r.result.id, r.result.first_name, None, r.result.username)

    def convert_message(self, msg):
        id = msg.message_id
        if msg.chat.id > 0:
            conversation = Conversation(msg.chat.id, msg.chat.first_name)
        else:
            conversation = Conversation(msg.chat.id, msg.chat.title)

        sender = User(msg['from'].id, msg['from'].first_name)
        if 'last_name' in msg['from']:
            sender.last_name = msg['from'].last_name
        if 'username' in msg['from']:
            sender.username = msg['from'].username

        # Gets the type of the message
        if 'text' in msg:
            type = 'text'
            content = msg.text
        else:
            type = None
            content = None

        date = msg.date

        if 'reply_to_message' in msg:
            reply = self.convert_message(msg.reply_to_message)
        else:
            reply = None

        extra = None

        return Message(id, conversation, sender, content, type, date, reply, extra)

    def receiver_worker(self):
        try:
            logging.debug('Starting receiver worker...')
            def get_updates(offset=None, limit=None, timeout=None):
                params = {}
                if offset:
                    params['offset'] = offset
                if limit:
                    params['limit'] = limit
                if timeout:
                    params['timeout'] = timeout
                return self.api_request('getUpdates', params)

            while self.bot.started:
                last_update = 0

                while (self.bot.started):
                    res = get_updates(last_update + 1)
                    if res:
                        result = res.result
                        for u in result:
                            if u.update_id > last_update:
                                last_update = u.update_id

                                if 'inline_query' in u:
                                    message = self.convert_inline(u.inline_query)
                                    self.bot.inbox.put(message)

                                elif 'message' in u:
                                    message = self.convert_message(u.message)
                                    self.bot.inbox.put(message)

                                elif 'edited_message' in u:
                                    message = self.convert_message(u.edited_message)
                                    self.bot.inbox.put(message)
        except KeyboardInterrupt:
            pass

    def send_message(self, message):
        if message.type == 'text':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "typing"})
            params = {
                "chat_id": message.conversation.id,
                "text": message.content,
                "disable_web_page_preview": True,
            }
            if message.extra and 'format' in message.extra:
                params['parse_mode'] = message.extra['format']

                self.api_request('sendMessage', params)

        elif message.type == 'photo':
            print('type photo')
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "upload_photo"})
            params = {
                "chat_id": message.conversation.id,
                "photo": message.content,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            files = None
            if not isinstance(message.content, string_types):
                files = {'photo': message.content}
            else:
                params['photo'] = message.content
            print('api send photo')
            self.api_request('sendPhoto', params, files=files)
        else:
            logging.debug("UNKNOWN MESSAGE TYPE")
