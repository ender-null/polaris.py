from core.utils import *
from mechanicalsoup import Browser

commands = [
    ('/waifu2x', [])
]
description = 'Single-Image Super-Resolution for Anime-Style Art using Deep Convolutional Neural Networks. And it supports photo.'


def run(m):
    if not m.reply:
        return send_message(m, lang.errors.reply)

    url = get_file(m.reply.content, only_url=True)
    scale = '1'
    noise = '2'
    style = 'art'
    
    browser = Browser(soup_config={"features":"html.parser"})
    page = browser.get("http://waifu2x.udp.jp")
    form = page.soup.find('form')
    form.find("input", {"name": "url"})["value"] = url
    form.find("input", {"name": "scale", "value": scale})["checked"] = ""
    form.find("input", {"name": "noise", "value": noise})["checked"] = ""
    form.find("input", {"name": "style", "value": style})["checked"] = ""

    send_message(m, lang.errors.wait)

    res = browser.submit(form, page.url)
    photo = save_to_file(res)

    if photo:
        send_photo(m, photo)
    else:
        send_message(m, lang.errors.download)
