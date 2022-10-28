from hoshino.typing import CQEvent
from hoshino.util import FreqLimiter, escape

from .. import chara
from . import sv

lmt = FreqLimiter(5)

@sv.on_prefix(('档案谁是'))
async def whois(bot, ev: CQEvent):
    name = escape(ev.message.extract_plain_text().strip())
    if not name:
        return
    id_ = chara.name2id(name)
    confi = 100
    guess = False
    if id_ == chara.UNKNOWN:
        id_, guess_name, confi = chara.guess_id(name)
        guess = True
    c = chara.fromid(id_)
    
    if confi < 60:
        return

    uid = ev.user_id
    if not lmt.check(uid):
        await bot.finish(ev, f'碧蓝档案花名册冷却中(剩余 {int(lmt.left_time(uid)) + 1}秒)', at_sender=True)

    # lmt.start_cd(uid, 120 if guess else 0)
    if guess:
        msg = f'碧蓝档案似乎没有叫"{name}"的人欸'
        await bot.send(ev, msg)
        msg = f'您有{confi}%的可能在找{guess_name} {c.icon.cqcode} {c.name}'
        await bot.send(ev, msg)
    else:
        msg = f'{c.icon.cqcode} {c.name}'
        await bot.send(ev, msg, at_sender=True)
