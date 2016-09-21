from polaris.types import Message, User
import time

def get_me(self):
    return User(0, self.name, None, self.name)

def convert_messages(msg):
    # Not needed in this sample connector.
    pass

def get_messages(self):
    m1 = Message(1, Message.Conversation(1), User(1), 'Hey I just met you', 'text')
    m2 = Message(1, Message.Conversation(1), User(1), 'And this is crazy', 'text')
    m3 = Message(1, Message.Conversation(1), User(1), 'But here\'s my number', 'text')
    m4 = Message(1, Message.Conversation(1), User(1), 'So call me maybe', 'text')

    self.inbox.put(m1)
    time.sleep(2)
    self.inbox.put(m2)
    time.sleep(2)
    self.inbox.put(m3)
    time.sleep(2)
    self.inbox.put(m4)
    time.sleep(60)

def send_message(self, message):
    pass
