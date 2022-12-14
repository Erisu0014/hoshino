import base64
import aiohttp
from bs4 import BeautifulSoup


# 从巴哈姆特论坛获取总力攻略图，获取方式比较粗糙，可能会取错帖子。
# 实现方法：获取当前总力战top1的帖子的第二张图片。
# todo: 如果总力攻略贴固定，可以整理出每个总力对应帖子的url来获取图片
async def get_raid_img():
    try:
        bbs_url = "https://forum.gamer.com.tw/B.php?bsn=38898&qt=2&subbsn=14"
        async with aiohttp.request('GET', url=bbs_url, allow_redirects=False) as resp:
            pageData = await resp.text()
        soup = BeautifulSoup(pageData, "html.parser")
        articleUrl = "https://forum.gamer.com.tw/" + str(soup.find("p", "b-list__main__title is-highlight").get("href"))
        async with aiohttp.request('GET', url=articleUrl, allow_redirects=False) as resp:
            article = await resp.text()
        soup = BeautifulSoup(article, "html.parser")
        image_url = soup.find_all("a", "photoswipe-image")[1].get("href")
        async with aiohttp.request('GET', url=image_url, allow_redirects=False) as resp:
            image_data = await resp.read()
        base64_str = f"base64://{base64.b64encode(image_data).decode()}"
        return base64_str
    except:
        return ""
