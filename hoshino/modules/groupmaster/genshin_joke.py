# -*- coding: utf-8 -*-
"""
@Time    : 2022/11/9 14:49
@Author  : 物述有栖
@File    : genshin_joke.py
@DES     : 
"""

import random

from genshin_joke_text import joke
from hoshino import Service

sv = Service('genshin_joke', visible=False)


# basic function for debug, not included in Service('chat')
@sv.on_keyword('我去 原', 'opssw', 'op', '原')
async def genshin_joke(session):
    await session.send(random.choice(joke))