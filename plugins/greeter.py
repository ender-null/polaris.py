from core.utils import *

commands = [
    ('^join_user$', []),
    ('^left_user$', [])
]
hidden = True

def run(m):
    if m.content == 'join_user':
        return send_message(m, 'Hello!')
    elif m.content == 'left_user':
        return send_message(m, 'Goodbye!')