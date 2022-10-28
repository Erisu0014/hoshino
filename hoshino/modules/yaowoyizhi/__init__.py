import base64
import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from hoshino import Service, aiorequests

sv = Service('ywyzm', enable_on_default=True)


def img_gen(pic):
    word1 = f'要我一直'
    word2 = f'吗'
    y = int(pic.size[1] * 600 / pic.size[0])
    y1 = int(pic.size[1] * 700 / pic.size[0] + 30)
    font = ImageFont.truetype('msyh.ttc', 100)
    im = Image.new('RGBA', (600, y1 if y1 > y + 150 else y + 150), (255, 255, 255, 255))
    draw = ImageDraw.Draw(im)
    img1 = pic.resize((600, y), Image.ANTIALIAS)
    img2 = pic.resize((100, int(y / 6)), Image.ANTIALIAS)
    im.paste(img1, (0, 0), img1)
    im.paste(img2, (400, int(y + (y1 - y - y / 6) / 2 if y1 > y + 150 else y + (150 - y / 6) / 2)))
    draw.text((0, y), word1, (0, 0, 0, 255), font)
    draw.text((500, y), word2, (0, 0, 0, 255), font)
    return im


@sv.on_prefix('要我一直')
async def ywyz(bot, ev):
    match = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
    if not match:
        return
    resp = await aiorequests.get(match.group(2))
    resp_cont = await resp.content
    pic = Image.open(BytesIO(resp_cont)).convert("RGBA")
    pic = img_gen(pic)
    buf = BytesIO()
    img = pic.convert('RGB')
    img.save(buf, format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ev, f'[CQ:image,file={base64_str}]')
