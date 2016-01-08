from utils import *
from PIL import Image, ImageFont, ImageDraw, ImageOps
# import images2gif
import PIL, os, random, time

commands = ['^rekt']
description = 'Get #rekt'

def run(msg):
    start = time.time()
    size = (320, 320) #changeable, should keep square
    frames = 20 #changeable

    def siz(n, xy=2): #original size = (640, 640) (all values are based on this)
        if xy == 2:
            return round(n / 640 * min(size))
        return round(n / 640 * size[xy])

    if 'reply_to_message' in msg:
        cid = msg['reply_to_message']['from']['id']
    else:
        cid = msg['from']['id']

    profile_photos = get_user_profile_photos(cid, limit=1)
    profile_photo = get_file(profile_photos['result']['photos'][0][-1]['file_id'])
    photo_url = 'https://api.telegram.org/file/bot' + get_token() + '/' + profile_photo['result']['file_path']
    rekt_photo = get_file('AgADBAADecMxGwzP1wABooeh2I_OfGfPvqYwAAQPK4h0YZD7xv3AAAIC')
    rekt_url = 'https://api.telegram.org/file/bot' + get_token() + '/' + rekt_photo['result']['file_path']

    rekt = Image.open(download(rekt_url).name).resize(size)
    user_photo = Image.open(download(photo_url).name).convert('RGB').resize(size)

    fonts = list()

    for font in [a for a in os.listdir(os.path.join('.', 'fonts')) if a.endswith('.ttf') or a.endswith('.otf')]:
        '''if font == 'WingDings.ttf': #deprecated code
            fonts.append(ImageFont.truetype(font, 128, encoding='symb'))
        else:
            fonts.append(ImageFont.truetype(font, 128))'''
        fonts.append(os.path.join('.', 'fonts', '')+font)
        print(font)

    results = list()
    for a0 in range(frames):
        #blend the user photo with rekt.jpg. random opacity
        alpha = random.randint(10, 90)/100
        result = Image.blend(rekt, user_photo, alpha)

        #blend the result with some color. random opacity and color
        alpha2 = random.randint(0, 50)/100
        color2 = (random.randint(0,255), random.randint(0,255),\
                  random.randint(0,255))
        colorfill = Image.new('RGB', size, color2)
        result = Image.blend(result, colorfill, alpha2)

        n = round(frames/2)
        a1 = random.randint(1, n) #more accurate randomness
        if a1 == 1: #2/frames == 1/n chance
            rng = 0
        else:
            rng = random.randint(1, 6)

        for a2 in range(rng):
            #print '#REKT'. random coordinates, color, size, font, angle and opacity
            color = (random.randint(0,255), random.randint(0,255),\
                     random.randint(0,255), random.randint(100, 255)) #last value is opacity
            fntsize = random.randint(siz(100), siz(156))
            fntindex = random.randint(1, len(fonts)) - 1
            fnt = ImageFont.truetype(fonts[fntindex], size=fntsize)
            fontsize = fnt.getsize('#REKT')

            for x in fontsize: #prevents errors when fntsize is large
                if x >= siz(640):
                    larger = True
                    break
                else:
                    larger = False

            if not larger:
                coord = (random.randint(0, (size[0]-fontsize[0])),\
                         random.randint(0, (size[1]-fontsize[1]))) #image size - fontsize = max coords (bottom right corner)
            else:
                coord = (size[0],size[1])
            rotation = random.randint(-30, 30) #-30º to 30º
            alpha3 = random.randint(70, 100) / 100


            #we print the text in a new image
            txt = Image.new('L', size) #white text over black background
            colorimg = Image.new('RGBA', size, color)
            d = ImageDraw.Draw(txt)
            d.text(coord, '#REKT', fill=color, font=fnt)

            txt = txt.rotate(rotation, expand=0, resample=PIL.Image.NEAREST).resize(size, resample=PIL.Image.NEAREST)
            result.paste(colorimg, mask=txt)
        #finally, we select a random square area to INTENSIFY
        x0 = random.randint(0, siz(140, 0))
        y0 = random.randint(0, siz(140, 1))
        x1 = x0 + siz(500)
        y1 = y0 + siz(500, 1)
        area = (x0, y0, x1, y1)
        result = result.crop(area).resize(size, resample=PIL.Image.NEAREST)
        #append the final image to a list, to make a gif
        results.append(result)

    rekt_gif = tempfile.NamedTemporaryFile(delete=False, suffix='.gif')
    images2gif.writeGif(rekt_gif, results, duration=0.11, repeat=True, dither=False, nq=0, subRectangles=False)

    '''for x in range(len(results)): #dump frames to directory
        results[x].save('result\\frame-'+str(x)+'.jpg')'''

    elapsed = time.time() - start
    print('\nDone in %s seconds.' %(elapsed))

    if rekt_gif:
        send_document(msg['chat']['id'], rekt_gif)
    else:
        send_error(msg, 'download')