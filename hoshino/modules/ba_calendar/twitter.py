import datetime
import base64
import json
from urllib.parse import quote
import tweepy
import hoshino
from hoshino.typing import CQEvent
from hoshino import aiorequests, priv

sv = hoshino.Service('ba_twitter', enable_on_default=False, visible=True, bundle='ba_twitter')

rep1 = {"ブルアカ": "Blue Archive"}  # 在日语时替换，防止结合语境的奇奇怪怪翻译
rep2 = {"\n\n": "\n", "\r\n\r\n": "\r\n", "蓝色档案": "碧蓝档案", "Blue 存档": "碧蓝档案", "皮卡招聘": "学生招募", "皮卡招募": "学生招募", "布鲁赤井部": "碧蓝档案"}  # 生草翻译强行替换，自行添加


def get_client():
    # 推特api密钥，自行获取填写
    bearer_token = ""
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""

    client = tweepy.Client(bearer_token=bearer_token,
                           access_token=access_token,
                           access_token_secret=access_token_secret,
                           consumer_key=consumer_key,
                           consumer_secret=consumer_secret)
    return client


async def translate(string, source="ja", target="zh-CN"):  # google翻译
    text = ""
    url = "http://43.246.208.221:9097/api/sentry/translate"
    data = "text=" + quote(string.encode("utf-8")) + "&source=" + source + "&target=" + target
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        rsp = await aiorequests.post(url, data=data, headers=headers, timeout=10)
        rsp = await rsp.text
        json_data = json.loads(rsp)
        text = json_data.get("data", "")
        if not text:
            error = json_data.get("error")
            print("【ERROR】" + error)
            return string  # 出问题返回原文
    except Exception as e:
        print("【Translate】Error : " + str(e))
        return string  # 出问题返回原文
    return text


async def im2base64str(img_url):
    img = await aiorequests.get(img_url)
    img_cont = await img.content
    base64_str = f"base64://{base64.b64encode(img_cont).decode()}"
    return base64_str


async def get_tweets(client):
    msg_list = []
    start_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=5.05)).isoformat("T")[:-4] + "Z"
    tweets = client.get_users_tweets(id=1237586987969687555, start_time=start_time,
                                     tweet_fields=['created_at', 'entities'], media_fields=["url", "preview_image_url"],
                                     expansions="attachments.media_keys", exclude=["retweets", "replies"])
    if not tweets.data:
        return msg_list

    media = {m["media_key"]: m for m in tweets.includes['media']} if "media" in tweets.includes else []
    for tweet in tweets.data:
        msg = ""
        text = str(tweet.text)
        for k, v in rep1.items():
            text = text.replace(k, v)
        text = await translate(text)  # 生草翻译，N114514可以注释此行
        for k, v in rep2.items():
            text = text.replace(k, v)
        msg = msg + text
        include_img = False
        if 'attachments' in tweet.data and 'media_keys' in tweet.data['attachments']:
            media_keys = tweet.data['attachments']['media_keys']
            for media_key in media_keys:
                if media[media_key].url and media[media_key].type == "photo":
                    b64img = await im2base64str(media[media_key].url)
                    msg = msg + f"\n[CQ:image,file={b64img}]"
                    include_img = True
                if media[media_key].preview_image_url:
                    b64img = await im2base64str(media[media_key].preview_image_url)
                    msg = msg + f"\n[CQ:image,file={b64img}]"
                    include_img = True
        if not include_img:  # 实在没图片了拿来凑数
            for url in tweet.entities['urls']:
                if 'images' in url:
                    b64img = await im2base64str(url['images'][0]['url'])
                    msg = msg + f"\n[CQ:image,file={b64img}]"
        msg_list.append(msg)
    return msg_list


@sv.scheduled_job('cron', minute='*/5')
async def send_tweet():
    bot = hoshino.get_bot()
    available_group = await sv.get_enable_groups()
    client = get_client()
    msg_list = await get_tweets(client)
    if len(msg_list) > 0:
        for group_id in available_group:
            for msg in msg_list:
                await bot.send_group_msg(group_id=int(group_id), message=msg)
