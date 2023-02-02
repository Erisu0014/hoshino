# -*- coding: utf-8 -*-
"""
@Time    : 2022/11/9 14:49
@Author  : 物述有栖
@File    : genshin_joke.py
@DES     : 
"""

import random

from .genshin_joke_text import joke
from hoshino import Service, R
from nonebot import CommandSession

sv = Service('genshin_joke', visible=False)


# basic function for debug, not included in Service('chat')
@sv.on_command('我去 原', aliases=('op', '叩', '我去 o', '我去 原！'))
async def genshin_joke(ss: CommandSession):
    result = random.choice(joke)
    if result[:3] == "pic":
        pic = R.img(f'op/{result[3:]}').cqcode
        await ss.send(pic)
    else:
        await ss.finish(result)
