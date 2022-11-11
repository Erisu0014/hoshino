# -*- coding: utf-8 -*-
"""
@Time    : 2022/11/9 14:49
@Author  : 物述有栖
@File    : genshin_joke.py
@DES     : 
"""

import random

from .genshin_joke_text import joke
from hoshino import Service
from nonebot import CommandSession

sv = Service('genshin_joke', visible=False)


# basic function for debug, not included in Service('chat')
@sv.on_command('我去 原',   aliases=('op','叩','我去 o','我去 原！'))
async def genshin_joke(ss: CommandSession):
    await ss.finish(random.choice(joke))
