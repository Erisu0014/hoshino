# ba_calendar
碧蓝档案图形化活动日历、官推转发、总力攻略图\汉化漫画获取插件, 适用于 HoshinoBot v2.  

项目地址 https://github.com/Cosmos01/ba_calendar  

参考项目：https://github.com/zyujs/pcr_calendar  

![FYBN %B61EG``_OG~B8XZ$B](https://user-images.githubusercontent.com/37209685/165712652-5b221387-f0cc-41c2-9b6c-9b6b76063ed5.PNG)
  
## 日程信息源
日服: [BiliWiki](https://wiki.biligame.com/bluearchive/%E9%A6%96%E9%A1%B5)  


国际服暂未找到稳定信息源，故暂时只支持日服



## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/Cosmos01/ba_calendar.git`
2. 进入本项目目录运行 `pip install -r requirements.txt `安装必要的第三方库
3. 申请推特API，在项目目录下的twitter.py中填入获取到的密钥等参数 (具体申请方法自行搜索)
4. 在 `config/__bot__.py`的MODULES_ON列表里加入 `ba_calendar`
5. 重启HoshinoBot  

模块默认都是关闭状态  
使用bot指令开启功能：  
- `启用 ba_twitter`(确认已经填写好密钥再开启)
- `启用 ba_calendar`
- `启用 ba_comic_cn`
- `ba日服日历 on`


## 指令列表
- `ba日历` : 查看本群订阅服务器日历
- `ba日服日历` : 查看指定服务器日程
- `ba日服日历 on/off` : 订阅/取消订阅指定服务器的日历推送
- `ba日历 time 时:分` : 设置日历推送时间
- `ba日历 status` : 查看本群日历推送设置
- `ba日历 cardimage` : (go-cqhttp限定)切换是否使用cardimage模式发送日历图片
- `总力一图流` : 获取当前总力攻略图片
