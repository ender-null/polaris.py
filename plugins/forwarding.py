from core.utils import *
from copy import deepcopy

hidden = True

def process(m):
    if has_tag(m.receiver.id, 'resend:?') or has_tag(m.receiver.id, 'fwd:?'):
        id = str(m.receiver.id)
        for tag in tags.list[id]:
            if tag.startswith('resend:'):
                cid = tag.split(':')[1]
                if m.type == 'photo' or m.type == 'document' or m.type == 'url':
                    r = deepcopy(m)
                    r.receiver = Group()
                    r.receiver.id = cid
                    
                    if m.type == 'photo':
                        send_photo(r, m.content)
                    elif m.type == 'document':
                        send_document(r, m.content)
                    elif m.type == 'url':
                        send_message(r, m.content, preview=True)


            elif tag.startswith('fwd:'):
                cid = tag.split(':')[1]
                if m.type == 'photo' or m.type == 'document' or m.type == 'url':
                    forward_message(cid, m)
