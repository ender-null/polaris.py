from polaris.types import Message, Conversation, User
from polaris.utils import send_request, catch_exception
from six import string_types
import logging, json


class bindings(object):
    def __init__(self, bot):
        self.bot = bot

    def api_request(self, api_method, params=None, headers=None, files=None):
        url = 'https://api.telegram.org/bot%s/%s' % (self.bot.config['bindings_token'], api_method)
        try:
            return send_request(url, params, headers, files, post=True)
        except:
            return None

    def get_me(self):
        r = self.api_request('getMe')
        if r:
            return User(r.result.id, r.result.first_name, None, r.result.username)

    def convert_message(self, msg):
        id = msg.message_id
        if msg.chat.id > 0:
            conversation = Conversation(msg.chat.id, msg.chat.first_name)
        else:
            conversation = Conversation(msg.chat.id, msg.chat.title)

        if 'from' in msg:
            sender = User(msg['from'].id, msg['from'].first_name)

            if 'last_name' in msg['from']:
                sender.last_name = msg['from'].last_name

            if 'username' in msg['from']:
                sender.username = msg['from'].username

        else:
            sender = Conversation(msg['chat'].id, msg['chat'].title)

        # Gets the type of the message
        extra = {}

        if 'text' in msg:
            type = 'text'
            content = msg.text

            if 'entities' in msg:
                for entity in msg.entities:
                    if entity.type == 'url':
                        if 'urls' not in extra:
                            extra['urls'] = []
                        extra['urls'].append(msg.text[entity.offset:entity.offset + entity.length])

        elif 'audio' in msg:
            type = 'audio'
            content = msg.audio.file_id
            extra['duration'] = msg.audio.duration
            if 'performer' in msg.audio:
                extra['performer'] = msg.audio.performer
            if 'title' in msg.audio:
                extra['title'] = msg.audio.title
            if 'mime_type' in msg.audio:
                extra['mime_type'] = msg.audio.mime_type
            if 'file_size' in msg.audio:
                extra['file_size'] = msg.audio.file_size

        elif 'document' in msg:
            type = 'document'
            content = msg.document.file_id
            if 'thumb' in msg.document:
                extra['thumbnail'] = msg.document.thumb.file_id
            if 'file_name' in msg.document:
                extra['file_name'] = msg.document.file_name
            if 'mime_type' in msg.document:
                extra['mime_type'] = msg.document.mime_type
            if 'file_size' in msg.document:
                extra['file_size'] = msg.document.file_size

        elif 'game' in msg:
            type = 'game'
            content = {
                'title': msg.game.title,
                'description': msg.game.description,
                'photo': msg.game.photo[-1].file_id,
            }

            if 'text' in msg.game:
                extra['text'] = msg.game.text

        elif 'photo' in msg:
            type = 'photo'
            content = msg.photo[-1].file_id
            if 'width' in msg.photo[-1]:
                extra['width'] = msg.photo[-1].width
            if 'height' in msg.photo[-1]:
                extra['height'] = msg.photo[-1].height
            if 'file_size' in msg.photo[-1]:
                extra['file_size'] = msg.photo[-1].file_size

        elif 'sticker' in msg:
            type = 'sticker'
            content = msg.sticker.file_id
            if 'width' in msg.sticker:
                extra['width'] = msg.sticker.width
            if 'height' in msg.sticker:
                extra['height'] = msg.sticker.height
            if 'file_size' in msg.sticker:
                extra['file_size'] = msg.sticker.file_size
            if 'emoji' in msg.sticker:
                extra['emoji'] = msg.sticker.emoji
            if 'thumb' in msg.sticker:
                extra['thumbnail'] = msg.sticker.thumb.file_id

        elif 'video' in msg:
            type = 'video'
            content = msg.video.file_id
            if 'width' in msg.video:
                extra['width'] = msg.video.width
            if 'height' in msg.video:
                extra['height'] = msg.video.height
            if 'file_size' in msg.video:
                extra['file_size'] = msg.video.file_size
            if 'duration' in msg.video:
                extra['duration'] = msg.video.duration
            if 'thumb' in msg.video:
                extra['thumbnail'] = msg.video.thumb.file_id
            if 'mime_type' in msg.video:
                extra['mime_type'] = msg.video.mime_type

        elif 'voice' in msg:
            type = 'voice'
            content = msg.voice.file_id
            if 'file_size' in msg.voice:
                extra['file_size'] = msg.voice.file_size
            if 'duration' in msg.voice:
                extra['duration'] = msg.voice.duration
            if 'mime_type' in msg.voice:
                extra['mime_type'] = msg.voice.mime_type

        elif 'contact' in msg:
            type = 'contact'
            content = msg.contact.phone_number
            if 'first_name' in msg.contact:
                extra['first_name'] = msg.contact.first_name
            if 'last_name' in msg.contact:
                extra['last_name'] = msg.contact.last_name
            if 'user_id' in msg.contact:
                extra['user_id'] = msg.contact.user_id

        elif 'location' in msg:
            type = 'location'
            content = {
                'longitude': msg.location.longitude,
                'latitude': msg.location.latitude
            }
        elif 'venue' in msg:
            type = 'venue'
            content = {
                'longitude': msg.venue.location.longitude,
                'latitude': msg.venue.location.latitude
            }
            if 'title' in msg.venue:
                extra['title'] = msg.venue.title
            if 'address' in msg.venue:
                extra['address'] = msg.venue.address
            if 'foursquare_id' in msg.venue:
                extra['foursquare_id'] = msg.venue.foursquare_id

        elif 'new_chat_member' in msg:
            type = 'notification'
            content = 'new_chat_member'
            extra = {
                'user': User(msg.new_chat_member.id, msg.new_chat_member.first_name)
            }

            if 'last_name' in msg.new_chat_member:
                extra['user'].last_name = msg.new_chat_member.last_name
            if 'username' in msg.new_chat_member:
                extra['user'].username = msg.new_chat_member.username

        elif 'left_chat_member' in msg:
            type = 'notification'
            content = 'left_chat_member'
            extra = {
                'user': User(msg.left_chat_member.id, msg.left_chat_member.first_name)
            }

            if 'last_name' in msg.left_chat_member:
                extra['user'].last_name = msg.left_chat_member.last_name
            if 'username' in msg.left_chat_member:
                extra['user'].username = msg.left_chat_member.username

        elif 'new_chat_photo' in msg:
            type = 'notification'
            content = 'new_chat_photo'
            extra = {
                'photo': msg.new_chat_photo[-1].file_id
            }

        elif 'delete_chat_photo' in msg:
            type = 'notification'
            content = 'delete_chat_photo'

        elif 'group_chat_created' in msg:
            type = 'notification'
            content = 'group_chat_created'

        elif 'supergroup_chat_created' in msg:
            type = 'notification'
            content = 'supergroup_chat_created'

        elif 'channel_chat_created' in msg:
            type = 'notification'
            content = 'channel_chat_created'

        elif 'migrate_to_chat_id' in msg:
            type = 'notification'
            content = 'upgrade_to_supergroup'
            extra = {
                'chat_id': msg.migrate_to_chat_id,
                'from_chat_id': msg.chat.id
            }

        elif 'pinned_message' in msg:
            type = 'notification'
            content = 'pinned_message'
            extra = {
                'message': self.convert_message(msg.pinned_message)
            }

        else:
            logging.error(msg)
            type = None
            content = None
            extra = None

        if 'caption' in msg:
            extra['caption'] = msg.caption

        date = msg.date

        if 'reply_to_message' in msg:
            reply = self.convert_message(msg.reply_to_message)
        else:
            reply = None

        return Message(id, conversation, sender, content, type, date, reply, extra)


    def convert_inline(self, msg):
        id = msg.id
        conversation = Conversation(msg['from'].id, msg['from'].first_name)

        sender = User(msg['from'].id, msg['from'].first_name)
        if 'last_name' in msg['from']:
            sender.last_name = msg['from'].last_name

        if 'username' in msg['from']:
            sender.username = msg['from'].username

        content = msg.query
        type = 'inline_query'
        date = None
        reply = None
        extra =  {'offset': msg.offset}

        return Message(id, conversation, sender, content, type, date, reply, extra)


    def receiver_worker(self):
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

        try:
            last_update = 0

            while self.bot.started:
                res = get_updates(last_update + 1)
                if res and 'result' in res:
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

                            elif 'channel_post' in u:
                                message = self.convert_message(u.channel_post)
                                self.bot.inbox.put(message)

                            elif 'edited_channel_post' in u:
                                message = self.convert_message(u.edited_channel_post)
                                self.bot.inbox.put(message)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            if self.bot.started:
                catch_exception(e, self.bot)



    def send_message(self, message):
        if message.type == 'text':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "typing"})
            params = {
                "chat_id": message.conversation.id,
                "text": message.content
            }
            if message.extra and 'format' in message.extra:
                params['parse_mode'] = message.extra['format']

            if message.extra and 'preview' in message.extra:
                params['disable_web_page_preview'] = not message.extra['preview']

            if message.reply:
                params['reply_to_message_id'] = message.reply

            if message.extra and 'force_reply' in message.extra:
                params['reply_markup'] = json.dumps({
                    'force_reply': message.extra['force_reply']
                })

            self.api_request('sendMessage', params)

        elif message.type == 'photo':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "upload_photo"})
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            if message.reply:
                params['reply_to_message_id'] = message.reply

            files = None
            if message.content.startswith('/'):
                photo = open(message.content, 'rb')
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

            if message.reply:
                params['reply_to_message_id'] = message.reply

            files = None
            if message.content.startswith('/'):
                audio = open(message.content, 'rb')
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

            if message.reply:
                params['reply_to_message_id'] = message.reply

            files = None
            if message.content.startswith('/'):
                document = open(message.content, 'rb')
                files = {'document': document}
            else:
                params['document'] = message.content

            self.api_request('sendDocument', params, files=files)

        elif message.type == 'sticker':
            params = {
                "chat_id": message.conversation.id,
            }

            if message.extra and 'caption' in message.extra:
                params['caption'] = message.extra['caption']

            if message.reply:
                params['reply_to_message_id'] = message.reply

            files = None
            if message.content.startswith('/'):
                sticker = open(message.content, 'rb')
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

            if message.reply:
                params['reply_to_message_id'] = message.reply

            files = None
            if message.content.startswith('/'):
                video = open(message.content, 'rb')
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

            if message.reply:
                params['reply_to_message_id'] = message.reply

            files = None
            if message.content.startswith('/'):
                voice = open(message.content, 'rb')
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

            if message.reply:
                params['reply_to_message_id'] = message.reply

            self.api_request('sendLocation', params)

        elif message.type == 'venue':
            self.api_request('sendChatAction', params={"chat_id": message.conversation.id, "action": "find_location"})
            params = {
                "chat_id": message.conversation.id,
                "latitude": message.content['latitude'],
                "longitude": message.content['longitude']
            }

            if message.reply:
                params['reply_to_message_id'] = message.reply

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

            if message.reply:
                params['reply_to_message_id'] = message.reply

            self.api_request('sendContact', params)

        elif message.type == 'inline_results':
            params = {
                "inline_query_id": message.id,
                "results": message.content
            }

            if message.extra and 'cache_time' in message.extra:
                params['cache_time'] = message.extra['cache_time']

            if message.extra and 'is_personal' in message.extra:
                params['is_personal'] = message.extra['is_personal']

            if message.extra and 'next_offset' in message.extra:
                params['next_offset'] = message.extra['next_offset']

            if message.extra and 'switch_pm_text' in message.extra:
                params['switch_pm_text'] = message.extra['switch_pm_text']

            if message.extra and 'switch_pm_parameter' in message.extra:
                params['switch_pm_parameter'] = message.extra['switch_pm_parameter']

            self.api_request('answerInlineQuery', params)

        else:
            logging.error("UNKNOWN MESSAGE TYPE: %s" % message.type)


    # THESE METHODS DO DIRECT ACTIONS #
    def get_file(self, file_id):
        return False


    def invite_conversation_member(self, conversation_id, user_id):
        return False


    def kick_conversation_member(self, conversation_id, user_id):
        params = {
            "chat_id": conversation_id,
            "user_id": user_id
        }
        result = self.api_request('kickChatMember', params)
        if result.ok == False:
            if result.description.split(': ')[1] == 'CHAT_ADMIN_REQUIRED' or result.description.split(': ')[1] == 'Not enough rights to kick participant':
                return None
            else:
                return False
        return True


    def unban_conversation_member(self, conversation_id, user_id):
        params = {
            "chat_id": conversation_id,
            "user_id": user_id
        }
        result = self.api_request('unbanChatMember', params)
        if result.ok == False:
            if result.description.split(': ')[1] == 'CHAT_ADMIN_REQUIRED' or result.description.split(': ')[1] == 'Not enough rights to kick participant':
                return None
            else:
                return False
        return True

    def conversation_info(self, conversation_id):
        params = {
            "chat_id": conversation_id
        }
        return self.api_request('getChat', params)
