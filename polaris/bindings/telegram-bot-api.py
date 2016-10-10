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
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "upload_photo"})
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            photo = open(message.content, 'rb')
            files = None
            if not isinstance(photo, string_types):
                files = {'photo': photo}
            else:
                params['photo'] = message.content

            self.api_request('sendPhoto', params, files=files)

        elif message.type == 'audio':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "upload_audio"})
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            audio = open(message.content, 'rb')
            files = None
            if not isinstance(photo, string_types):
                files = {'audio': audio}
            else:
                params['audio'] = message.content

            self.api_request('sendAudio', params, files=files)

        elif message.type == 'document':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "upload_document"})
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            document = open(message.content, 'rb')
            files = None
            if not isinstance(photo, string_types):
                files = {'document': document}
            else:
                params['document'] = message.content

            self.api_request('sendDocument', params, files=files)

        elif message.type == 'photo':
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            sticker = open(message.content, 'rb')
            files = None
            if not isinstance(sticker, string_types):
                files = {'sticker': sticker}
            else:
                params['sticker'] = message.content

            self.api_request('sendSticker', params, files=files)

        elif message.type == 'video':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "upload_video"})
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            video = open(message.content, 'rb')
            files = None
            if not isinstance(video, string_types):
                files = {'video': video}
            else:
                params['video'] = message.content

            self.api_request('sendVideo', params, files=files)

        elif message.type == 'voice':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "record_audio"})
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            voice = open(message.content, 'rb')
            files = None
            if not isinstance(voice, string_types):
                files = {'voice': voice}
            else:
                params['voice'] = message.content

            self.api_request('sendVoice', params, files=files)

        elif message.type == 'location':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "find_location"})
            params = {
                "chat_id": message.conversation.id,
                "latitude": message.content['latitude'],
                "longitude": message.content['longitude']
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            self.api_request('sendLocation', params)

        elif message.type == 'venue':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "find_location"})
            params = {
                "chat_id": message.conversation.id,
                "latitude": message.content['latitude'],
                "longitude": message.content['longitude']
            }

            if message.extra:
                if 'caption' in message.extra:
                    params['caption'] = message.extra['caption']

                if 'title' in message.extra:
                    params['title'] = message.extra['title']

                if 'address' in message.extra:
                    params['address'] = message.extra['address']

            self.api_request('sendVenue', params)

        elif message.type == 'contact':
            params = {
                "chat_id": message.conversation.id,
                "phone_number": message.content['phone_number'],
                "first_name": message.content['first_name']
            }

            if message.extra and 'last_name' in message.extra:
                params['last_name'] = message.extra['last_name']

            self.api_request('sendContact', params)

        else:
            logging.debug("UNKNOWN MESSAGE TYPE: %s" % message.type)
