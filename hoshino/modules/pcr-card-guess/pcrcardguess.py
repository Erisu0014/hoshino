import asyncio
import math
import os
import random
import sqlite3

from nonebot import MessageSegment

import hoshino
from hoshino import Service, util, R, priv
from hoshino.modules.priconne import chara
from hoshino.typing import CQEvent

sv = Service('card', bundle='pcr娱乐', help_='''
猜卡面 | 猜猜机器人随机发送的头像的一小部分来自哪位角色
猜卡面群排行 | 显示猜卡面小游戏猜对次数的群排行榜(只显示前十名)
'''.strip())
icon = {}

PIC_SIDE_LENGTH = 210
ONE_TURN_TIME = 20
BASE_WIN_COIN = 175
RANK_WIN_COIN = 50
GET_COIN_CD = 60 * 60
DB_PATH = os.path.expanduser('~/.hoshino/pcr_card_guess_winning_counter.db')
BLACKLIST_ID = [1000, 1072, 1908, 4031, 9000, 1069, 1073, 1701, 1702, 1067, 1907, 1909, 1910, 1911, 1913, 1914, 1915,
                1916, 1917, 1918, 1919, 1920, 9601, 9602, 9603, 9604]  # 黑名单ID
answered_players = []
answered_right_players = []
get_coin_limiter = util.FreqLimiter(GET_COIN_CD)


class WinnerJudger:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_chara_id = {}

    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)

    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def set_correct_chara_id(self, gid, cid):
        self.correct_chara_id[gid] = cid

    def get_correct_chara_id(self, gid):
        return self.correct_chara_id[gid] if self.correct_chara_id.get(gid) is not None else chara.UNKNOWN

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_chara_id[gid] = chara.UNKNOWN


winner_judger = WinnerJudger()


class WinningCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()

    def _connect(self):
        return sqlite3.connect(DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS CARDWINNINGCOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           COUNT           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _record_winning(self, gid, uid):
        try:
            winning_number = self._get_winning_number(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO CARDWINNINGCOUNTER (GID,UID,COUNT) \
                                VALUES (?,?,?)", (gid, uid, winning_number + 1))
            conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _get_winning_number(self, gid, uid):
        try:
            r = self._connect().execute("SELECT COUNT FROM CARDWINNINGCOUNTER WHERE GID=? AND UID=?",
                                        (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')


async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card'] != '' else m['nickname']
    return d


def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]


@sv.on_fullmatch(('猜卡面排行榜', '猜卡面群排行'))
async def description_guess_group_ranking(bot, ev: CQEvent):
    try:
        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        card_winningcount_dict = {}
        winning_counter = WinningCounter()
        for uid in user_card_dict.keys():
            if uid != ev.self_id:
                card_winningcount_dict[user_card_dict[uid]] = winning_counter._get_winning_number(ev.group_id, uid)
        group_ranking = sorted(card_winningcount_dict.items(), key=lambda x: x[1], reverse=True)
        msg = '猜卡面小游戏此群排行为:\n'
        for i in range(min(len(group_ranking), 10)):
            if group_ranking[i][1] != 0:
                msg += f'第{i + 1}名: {group_ranking[i][0]}, 猜对次数: {group_ranking[i][1]}次\n'
        await bot.send(ev, msg.strip())
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_fullmatch('重置猜卡面')
async def reset_vatar_guess(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '¿')
        return
    winner_judger.turn_off(ev.group_id)
    answered_players.clear()
    answered_right_players.clear()


@sv.on_fullmatch('猜卡面')
async def card_guess(bot, ev: CQEvent):
    if winner_judger.get_on_off_status(ev.group_id):
        await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
        return
    winner_judger.turn_on(ev.group_id)
    answered_players.clear()
    answered_right_players.clear()
    dir_path = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'priconne', 'card')
    files = os.listdir(dir_path)
    filename = random.choice(files)
    chara_id = int(filename[0:4])
    winner_judger.set_correct_chara_id(ev.group_id, chara_id)
    c = chara.fromid(chara_id)
    global card_img
    card_img = R.img(os.path.join('priconne', 'card', filename))
    img = card_img.open()
    left = math.floor(random.random() * (1408 - PIC_SIDE_LENGTH))
    upper = math.floor(random.random() * (792 - PIC_SIDE_LENGTH))
    cropped = img.crop((left, upper, left + PIC_SIDE_LENGTH, upper + PIC_SIDE_LENGTH))
    cropped = MessageSegment.image(util.pic2b64(cropped))
    msg = f'猜猜这个图片是哪位角色卡面的一部分?({ONE_TURN_TIME}s后公布答案){cropped}'
    await bot.send(ev, msg)
    await asyncio.sleep(ONE_TURN_TIME)
    winning_counter = WinningCounter()
    msg = ''
    if len(answered_right_players) > 0:
        for i, u in enumerate(answered_right_players):
            winning_counter._record_winning(ev.group_id, u)
            winning_count = winning_counter._get_winning_number(ev.group_id, u)
            at_user = MessageSegment.at(u)
            msg += f'{at_user}猜对了，真厉害！TA已经猜对{winning_count}次了~\n'
        msg += f'正确答案是: {c.name}{card_img.cqcode}'
        answered_players.clear()
        answered_right_players.clear()
        winner_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    else:
        c = chara.fromid(winner_judger.get_correct_chara_id(ev.group_id))
        msg = f'正确答案是: {c.name}{card_img.cqcode}\n很遗憾，没有人答对~'
        answered_players.clear()
        answered_right_players.clear()
        winner_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return


COIN = 75


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    try:
        if winner_judger.get_on_off_status(ev.group_id):
            s = ev.message.extract_plain_text()
            cid = chara.name2id(s)
            if ev.user_id in answered_players and cid != chara.UNKNOWN:
                await bot.send(ev, f'你已经回答过惹', at_sender=True)
                return
            else:
                if (cid != chara.UNKNOWN):
                    answered_players.append(ev.user_id)
                if cid != chara.UNKNOWN and cid == winner_judger.get_correct_chara_id(
                        ev.group_id) and winner_judger.get_winner(ev.group_id) == '':
                    gid, uid = ev.group_id, ev.user_id
                    answered_right_players.append(uid)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))
