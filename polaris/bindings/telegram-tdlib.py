import json
import logging

from polaris.types import Conversation, Message, User
from polaris.utils import (catch_exception, download, is_int, send_request,
                           set_data)
from telegram.client import Telegram


class bindings(object):
    def __init__(self, bot):
        self.bot = bot
        self.no_threads = True
        if self.bot.config['bindings_token'].startswith('+'):
            self.client = Telegram(
                api_id=self.bot.config['api_keys']['telegram_app_id'],
                api_hash=self.bot.config['api_keys']['telegram_api_hash'],
                phone=self.bot.config['bindings_token'],
                database_encryption_key=self.bot.config['api_keys']['database_encryption_key']
            )
        else:
            self.client = Telegram(
                api_id=self.bot.config['api_keys']['telegram_app_id'],
                api_hash=self.bot.config['api_keys']['telegram_api_hash'],
                bot_token=self.bot.config['bindings_token'],
                database_encryption_key=self.bot.config['api_keys']['database_encryption_key']
            )
        self.client.login()

    def get_me(self):
        result = self.client.get_me()
        result.wait()
        me = result.update
        return User(me['id'], me['first_name'], me['last_name'], me['username'], me['type']['@type'] == 'userTypeBot')

    def api_request(self, api_method, params=None, headers=None, data=None, files=None):
        url = 'https://api.telegram.org/bot{}/{}'.format(
            self.bot.config['bindings_token'], api_method)
        try:
            return send_request(url, params, headers, files, data, post=True, bot=self.bot)
        except:
            return None

    def start(self):
        if not self.bot.info.is_bot:
            # result = self.client.get_chats()
            data = {
                '@type': 'getChats',
                'chat_list': {'@type': 'chatListMain'},
                'offset_order': '9223372036854775807',
                'offset_chat_id': 0,
                'limit': 100,
            }

            result = self.client._send_data(data)
            result.wait()

            if result.error:
                self.bot.send_alert(result.error_info)
                self.bot.send_alert(data)

        def new_message_handler(update):
            if update['message']['is_outgoing']:
                return

            data = {
                '@type': 'viewMessages',
                'chat_id': update['message']['chat_id'],
                'message_ids': [update['message']['id']],
                'force_read': True
            }
            result = self.client._send_data(data)
            result.wait()

            if 'message' in update:
                msg = self.convert_message(update['message'])

                try:
                    logging.info(
                        '[{}] {}@{} [{}] sent [{}] {}'.format(msg.sender.id, msg.sender.first_name, msg.conversation.title, msg.conversation.id, msg.type, msg.content))
                except AttributeError:
                    logging.info(
                        '[{}] {}@{} [{}] sent [{}] {}'.format(msg.sender.id, msg.sender.title, msg.conversation.title, msg.conversation.id, msg.type, msg.content))
                try:
                    if msg.content.startswith('/') or msg.content.startswith(self.bot.config.prefix):
                        self.send_chat_action(msg.conversation.id)
                    self.bot.on_message_receive(msg)
                    self.cancel_send_chat_action(msg.conversation.id)
                    while self.bot.outbox.qsize() > 0:
                        msg = self.bot.outbox.get()
                        logging.info(' [{}] {}@{} [{}] sent [{}] {}'.format(msg.sender.id, msg.sender.first_name,
                                                                            msg.conversation.title, msg.conversation.id, msg.type, msg.content))
                        self.send_message(msg)

                except KeyboardInterrupt:
                    pass

                except Exception as e:
                    logging.error(e)
                    if self.bot.started:
                        catch_exception(e, self.bot)

        self.client.add_message_handler(new_message_handler)

    def convert_message(self, msg):
        try:
            # logging.info(msg)
            id = msg['id']
            extra = {}

            request = self.client.get_chat(msg['chat_id'])
            request.wait()
            raw_chat = request.update

            conversation = Conversation(int(msg['chat_id']))
            if raw_chat and 'title' in raw_chat:
                conversation.title = raw_chat['title']

            if msg['sender_user_id'] > 0:
                request = self.client.get_user(msg['sender_user_id'])
                request.wait()
                raw_sender = request.update

                sender = User(int(msg['sender_user_id']))
                if 'first_name' in raw_sender:
                    sender.first_name = str(raw_sender['first_name'])
                if 'last_name' in raw_sender:
                    sender.last_name = str(raw_sender['last_name'])
                if 'username' in raw_sender:
                    sender.username = str(raw_sender['username'])

            else:
                sender = User(conversation.id, conversation.title)

            if msg['content']['@type'] == 'messageText':
                content = msg['content']['text']['text']
                type = 'text'

                if 'entities' in msg['content']['text']:
                    for entity in msg['content']['text']['entities']:
                        if entity['type']['@type'] == 'textEntityTypeUrl':
                            if 'urls' not in extra:
                                extra['urls'] = []
                            extra['urls'].append(
                                content[entity['offset']:entity['offset'] + entity['length']])

                        elif entity['type']['@type'] == 'textEntityTypeMention':
                            if 'mentions' not in extra:
                                extra['mentions'] = []
                            extra['mentions'].append(
                                content[entity['offset']:entity['offset'] + entity['length']])

                        elif entity['type']['@type'] == 'textEntityTypeMentionText':
                            if 'mentions' not in extra:
                                extra['mentions'] = []
                            extra['mentions'].append(entity['user']['id'])

                        elif entity['type']['@type'] == 'textEntityTypeHashtag':
                            if 'hashtags' not in extra:
                                extra['hashtags'] = []
                            extra['hashtags'].append(
                                content[entity['offset']:entity['offset'] + entity['length']])

                        elif entity['type']['@type'] == 'textEntityTypeCashtag':
                            if 'cashtags' not in extra:
                                extra['cashtags'] = []
                            extra['cashtags'].append(
                                content[entity['offset']:entity['offset'] + entity['length']])

                        elif entity['type']['@type'] == 'textEntityTypeBotCommand':
                            if 'commands' not in extra:
                                extra['commands'] = []
                            extra['commands'].append(
                                content[entity['offset']:entity['offset'] + entity['length']])

                        elif entity['type']['@type'] == 'textEntityTypeEmailAddress':
                            if 'emails' not in extra:
                                extra['emails'] = []
                            extra['emails'].append(
                                content[entity['offset']:entity['offset'] + entity['length']])

                        elif entity['type']['@type'] == 'textEntityTypePhoneNumber':
                            if 'phone_numbers' not in extra:
                                extra['phone_numbers'] = []
                            extra['phone_numbers'].append(
                                content[entity['offset']:entity['offset'] + entity['length']])

            elif msg['content']['@type'] == 'messagePhoto':
                content = msg['content']['photo']['sizes'][0]['photo']['remote']['id']
                type = 'photo'
                if msg['content']['caption']:
                    extra['caption'] = msg['content']['caption']

            elif msg['content']['@type'] == 'messageAnimation':
                content = msg['content']['animation']['animation']['remote']['id']
                type = 'animation'
                if msg['content']['caption']:
                    extra['caption'] = msg['content']['caption']

            elif msg['content']['@type'] == 'messageDocument':
                content = msg['content']['document']['document']['remote']['id']
                type = 'document'
                if msg['content']['caption']:
                    extra['caption'] = msg['content']['caption']

            elif msg['content']['@type'] == 'messageAudio':
                content = msg['content']['audio']['audio']['remote']['id']
                type = 'audio'
                if msg['content']['caption']:
                    extra['caption'] = msg['content']['caption']

            elif msg['content']['@type'] == 'messageVideo':
                content = msg['content']['video']['video']['remote']['id']
                type = 'video'
                if msg['content']['caption']:
                    extra['caption'] = msg['content']['caption']

            elif msg['content']['@type'] == 'messageVoiceNote':
                content = msg['content']['voice_note']['voice']['remote']['id']
                type = 'voice'
                if msg['content']['caption']:
                    extra['caption'] = msg['content']['caption']

            elif msg['content']['@type'] == 'messageSticker':
                content = msg['content']['sticker']['sticker']['remote']['id']
                type = 'sticker'

            elif msg['content']['@type'] == 'messageChatAddMembers':
                content = 'new_chat_member'
                type = 'notification'

                request = self.client.get_user(
                    msg['content']['member_user_ids'][0])
                request.wait()
                raw_user = request.update

                extra = {
                    'user': User(int(msg['content']['member_user_ids'][0]))
                }
                if raw_user:
                    if 'first_name' in raw_user:
                        extra['user'].first_name = str(raw_user['first_name'])
                    if 'last_name' in raw_user:
                        extra['user'].last_name = str(raw_user['last_name'])
                    if 'username' in raw_user:
                        extra['user'].username = str(raw_user['username'])

            elif msg['content']['@type'] == 'messageChatJoinByLink':
                content = 'new_chat_member'
                type = 'notification'

                extra = {
                    'user': sender
                }

            elif msg['content']['@type'] == 'messageChatDeleteMember':
                content = 'left_chat_member'
                type = 'notification'

                request = self.client.get_user(msg['content']['user_id'])
                request.wait()
                raw_user = request.update

                extra = {
                    'user': User(int(msg['content']['user_id']))
                }
                if raw_user:
                    if 'first_name' in raw_user:
                        extra['user'].first_name = str(raw_user['first_name'])
                    if 'last_name' in raw_user:
                        extra['user'].last_name = str(raw_user['last_name'])
                    if 'username' in raw_user:
                        extra['user'].username = str(raw_user['username'])

            else:
                content = '[UNSUPPORTED]'
                type = 'text'

            reply = None
            if 'reply_to_message_id' in msg and msg['reply_to_message_id'] > 0:
                data = {
                    '@type': 'getMessage',
                    'chat_id': msg['chat_id'],
                    'message_id': msg['reply_to_message_id']
                }
                result = self.client._send_data(data)
                result.wait()
                if result.update:
                    reply = self.convert_message(result.update)

            date = msg['date']

            return Message(id, conversation, sender, content, type, date, reply, extra)

        except Exception as e:
            logging.error(e)
            catch_exception(e, self.bot)

    def convert_inline(self, msg):
        pass

    def receiver_worker(self):
        logging.debug('Starting receiver worker...')

    def send_message(self, message):
        try:
            self.send_chat_action(message.conversation.id, message.type)
            data = None
            input_message_content = None

            if message.type == 'text':
                if not message.content or len(message.content) == 0:
                    return

                if message.extra and 'format' in message.extra:
                    if message.extra['format'] == 'HTML':
                        parse_mode = 'textParseModeHTML'
                    else:
                        parse_mode = 'textParseModeMarkdown'

                    formated_text = self.client._send_data({
                        '@type': 'parseTextEntities',
                        'text': message.content,
                        'parse_mode': {
                            '@type': parse_mode
                        }
                    })
                    formated_text.wait()
                    if formated_text.update:
                        text = formated_text.update
                    else:
                        text = {
                            '@type': 'formattedText',
                            'text': message.content,
                            'entities': []
                        }
                else:
                    text = {
                        '@type': 'formattedText',
                        'text': message.content,
                        'entities': []
                    }

                preview = False
                if message.extra and 'preview' in message.extra:
                    preview = message.extra['preview']

                input_message_content = {
                    '@type': 'inputMessageText',
                    'text': text,
                    'disable_web_page_preview': not preview
                }

            elif message.type == 'photo':
                input_message_content = {
                    '@type': 'inputMessagePhoto',
                    'photo': self.get_input_file(message.content)
                }

                if message.extra and 'caption' in message.extra:
                    input_message_content['caption'] = {
                        '@type': 'formattedText',
                        'text': message.extra['caption']
                    }

            elif message.type == 'audio':
                input_message_content = {
                    '@type': 'inputMessageAudio',
                    'audio': self.get_input_file(message.content)
                }

                if message.extra and 'caption' in message.extra:
                    input_message_content['caption'] = {
                        '@type': 'formattedText',
                        'text': message.extra['caption']
                    }

            elif message.type == 'document':
                input_message_content = {
                    '@type': 'inputMessageDocument',
                    'document': self.get_input_file(message.content)
                }

                if message.extra and 'caption' in message.extra:
                    input_message_content['caption'] = {
                        '@type': 'formattedText',
                        'text': message.extra['caption']
                    }

            elif message.type == 'sticker':
                input_message_content = {
                    '@type': 'inputMessageSticker',
                    'sticker': self.get_input_file(message.content)
                }

            elif message.type == 'video':
                input_message_content = {
                    '@type': 'inputMessageVideo',
                    'video': self.get_input_file(message.content)
                }

            elif message.type == 'voice':
                input_message_content = {
                    '@type': 'inputMessageVoiceNote',
                    'voice_note': self.get_input_file(message.content)
                }

                if message.extra and 'caption' in message.extra:
                    input_message_content['caption'] = {
                        '@type': 'formattedText',
                        'text': message.extra['caption']
                    }

            elif message.type == 'forward':
                data = {
                    '@type': 'forwardMessages',
                    'chat_id': message.extra['conversation'],
                    'from_chat_id': message.conversation.id,
                    'message_ids': [message.extra['message']]
                }

            elif message.type == 'system':
                data = {
                    '@type': message.content,
                    'chat_id': message.conversation.id
                }

                if message.extra and 'title' in message.extra:
                    data['title'] = message.extra['title']

                if message.extra and 'user_id' in message.extra:
                    data['user_id'] = message.extra['user_id']

                if message.extra and 'custom_title' in message.extra:
                    data['custom_title'] = message.extra['custom_title']

                if message.extra and 'photo' in message.extra:
                    data['photo'] = self.get_input_file(message.extra['photo'])

                if message.extra and 'description' in message.extra:
                    data['description'] = message.extra['description']

                if message.extra and 'message_id' in message.extra:
                    data['message_id'] = message.extra['message_id']

                if message.extra and 'sticker_set_name' in message.extra:
                    data['sticker_set_name'] = message.extra['sticker_set_name']

                if message.extra and 'commands' in message.extra:
                    data['commands'] = message.extra['commands']

            elif message.type == 'api':
                files = None
                params = {
                    "chat_id": message.conversation.id,
                }

                if message.extra and 'user_id' in message.extra:
                    params['user_id'] = message.extra['user_id']

                if message.extra and 'custom_title' in message.extra:
                    params['custom_title'] = message.extra['custom_title']

                if message.extra and 'photo' in message.extra:
                    if message.extra['photo'].startswith('/'):
                        photo = open(message.extra['photo'], 'rb')
                        files = {'photo': photo}
                    else:
                        params['photo'] = message.extra['photo']

                if message.extra and 'message_id' in message.extra:
                    params['message_id'] = message.extra['message_id']

                if message.extra and 'sticker_set_name' in message.extra:
                    params['sticker_set_name'] = message.extra['sticker_set_name']

                if message.extra and 'commands' in message.extra:
                    params['commands'] = message.extra['commands']

                self.api_request(message.content, params, files=files)
                self.cancel_send_chat_action(message.conversation.id)
                return

            if input_message_content:
                data = {
                    '@type': 'sendMessage',
                    'chat_id': message.conversation.id,
                    'input_message_content': input_message_content
                }

                if message.reply:
                    data['reply_to_message_id'] = message.reply

            if data:
                result = self.client._send_data(data)

                result.wait()
                self.cancel_send_chat_action(message.conversation.id)

                if result.error:
                    self.request_processing(data, result.error_info)

                elif message.type == 'system':
                    self.bot.send_alert(result.update)
                    self.bot.send_alert(data)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            logging.error(e)
            if self.bot.started:
                catch_exception(e, self.bot)

    def get_input_file(self, content):
        if content.startswith('/'):
            return {
                '@type': 'inputFileLocal',
                'path': content
            }
        elif content.startswith('http'):
            return {
                '@type': 'inputFileRemote',
                'id': content
            }

        elif is_int(content):
            return {
                '@type': 'inputFileId',
                'id': content
            }

        else:
            return {
                '@type': 'inputFileRemote',
                'id': content
            }

    def send_chat_action(self, conversation_id, type='text'):
        action = 'chatActionTyping'

        if type == 'photo':
            action = 'chatActionUploadingPhoto'

        elif type == 'document':
            action = 'chatActionUploadingDocument'

        elif type == 'video':
            action = 'chatActionUploadingVideo'

        elif type == 'voice' or type == 'audio':
            action = 'chatActionRecordingVoiceNote'

        elif type == 'location' or type == 'venue':
            action = 'chatActionChoosingLocation'

        data = {
            '@type': 'sendChatAction',
            'chat_id': conversation_id,
            'action': {'@type': action}
        }
        result = self.client._send_data(data)
        result.wait()

    def cancel_send_chat_action(self, conversation_id):
        data = {
            '@type': 'sendChatAction',
            'chat_id': conversation_id,
            'action': {'@type': 'chatActionCancel'}
        }
        result = self.client._send_data(data)
        result.wait()

    def request_processing(self, request, response):
        self.bot.send_alert(request)
        self.bot.send_alert(response)

        leave_list = ['no rights', 'no write access',
                      'not enough rights to send', 'need administrator rights', 'CHANNEL_PRIVATE']

        for term in leave_list:
            if term in response['message']:
                self.bot.send_admin_alert('Leaving chat: {} [{}]'.format(
                    self.bot.groups[str(request['chat_id'])].title, request['chat_id']))
                res = self.bot.bindings.kick_conversation_member(
                    request['chat_id'], self.bot.info.id)
                self.bot.send_admin_alert(res)
                break

    # THESE METHODS DO DIRECT ACTIONS #
    def get_message(self, chat_id, message_id):
        data = {
            '@type': 'getMessage',
            'chat_id': chat_id,
            'message_id': message_id
        }
        result = self.client._send_data(data)
        result.wait()
        if result.update:
            return self.convert_message(result.update)

        return None

    def delete_message(self, chat_id, message_id):
        data = {
            '@type': 'deleteMessages',
            'chat_id': chat_id,
            'message_ids': [message_id],
            'revoke': True
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            return False
        return True

    def get_file(self, file_id, link=False):
        if self.bot.info.is_bot:
            params = {
                "file_id": file_id
            }
            result = self.api_request('getFile', params)
            if link:
                return 'https://api.telegram.org/file/bot{}/{}'.format(self.bot.config['bindings_token'], result.result.file_path)
            else:
                return download('https://api.telegram.org/file/bot{}/{}'.format(self.bot.config['bindings_token'], result.result.file_path))

        return None

    def join_by_invite_link(self, invite_link):
        if not self.bot.info.is_bot:
            data = {
                '@type': 'joinChatByInviteLink',
                'invite_link': invite_link
            }
            result = self.client._send_data(data)
            result.wait()

            if result.error_info:
                self.bot.send_alert(result.error_info)
                self.bot.send_alert(data)
                return False
            return True
        return None

    def invite_conversation_member(self, conversation_id, user_id):
        if self.bot.info.is_bot:
            return False

        data = {
            '@type': 'addChatMember',
            'chat_id': conversation_id,
            'user_id': user_id
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)
            return False
        return True

    def promote_conversation_member(self, conversation_id, user_id):
        data = {
            '@type': 'setChatMemberStatus',
            'chat_id': conversation_id,
            'user_id': user_id,
            'status': {'@type': 'chatMemberStatusAdministrator'}
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)
            return False
        return True

    def kick_conversation_member(self, conversation_id, user_id):
        data = {
            '@type': 'setChatMemberStatus',
            'chat_id': conversation_id,
            'user_id': user_id,
            'status': {'@type': 'chatMemberStatusLeft'}
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)
            return False
        return True

    def unban_conversation_member(self, conversation_id, user_id):
        data = {
            '@type': 'setChatMemberStatus',
            'chat_id': conversation_id,
            'user_id': user_id,
            'status': {'@type': 'chatMemberStatusMember'}
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)
            return False
        return True

    def rename_conversation(self, conversation_id, title):
        data = {
            '@type': 'setChatTitle',
            'chat_id': conversation_id,
            'title': title
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)
            return False
        return True

    def change_conversation_description(self, conversation_id, description):
        data = {
            '@type': 'setChatDescription',
            'chat_id': conversation_id,
            'description': description
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)
            return False
        return True

    def change_conversation_photo(self, conversation_id, photo):
        data = {
            '@type': 'setChatPhoto',
            'chat_id': conversation_id,
            'photo': photo
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)
            return False
        return True

    def conversation_info(self, conversation_id):
        data = {
            '@type': 'getChat',
            'chat_id': conversation_id
        }
        result = self.client._send_data(data)
        result.wait()
        self.bot.send_alert(result.update)

        return result.update

    def get_chat_administrators(self, conversation_id):
        data = {
            '@type': 'getChatAdministrators',
            'chat_id': conversation_id
        }
        result = self.client._send_data(data)
        result.wait()

        if result.error_info:
            self.bot.send_alert(result.error_info)
            self.bot.send_alert(data)

        admins = []
        if result.update and 'administrators' in result.update:
            for member in result.update['administrators']:
                user = User(member['user_id'])

                request = self.client.get_user(user.id)
                request.wait()
                raw_user = request.update

                if raw_user:
                    user.is_bot = raw_user['type']['@type'] == 'userTypeBot'
                    if 'first_name' in raw_user:
                        user.first_name = str(raw_user['first_name'])
                    if 'last_name' in raw_user:
                        user.last_name = str(raw_user['last_name'])
                    if 'username' in raw_user:
                        user.username = str(raw_user['username'])

                admins.append(user)

        return admins
