# main.py
import re

import werobot
from loguru import logger
import tornado.ioloop
import tornado.web
from werobot.contrib.tornado import make_handler
from apscheduler.schedulers.tornado import TornadoScheduler
# CONFIG PART
global TOKEN
global APP_ID
global APP_SECRET
global CHANNEL
global CHANNEL_ID
global CHANNEL_URL
TOKEN=""
APP_ID=""
APP_SECRET=""

CHANNEL=["本科生院-教务公告通知","本科生院-教务教学动态","研究生院-动态通知"]
CHANNEL_ID={"本科生院-教务公告通知":102,"本科生院-教务教学动态":103,"研究生院-动态通知":104}
CHANNEL_URL={"本科生院-教务公告通知":"https://rss.shab.fun/nju/jw/ggtz","本科生院-教务教学动态":"https://rss.shab.fun/nju/jw/jxdt","研究生院-动态通知":"https://rss.shab.fun/nju/gra"}
# ===
logger.info("booting njuhelper-x ...")
logger.info("starting scheduler ...")

import rss_source

logger.info("setting up robot ...")

robot = werobot.WeRoBot(token=TOKEN)
robot.config["APP_ID"] = APP_ID
robot.config["APP_SECRET"] = APP_SECRET
robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 80
client = robot.client

# njuhelper-x 需要建立公众号标签，分组名为CHANNEL中各个频道的名字，把各个频道的ID依次填进CHANNEL_ID
# 定义所需的各种方法

@robot.filter(re.compile("订阅 (.*)"))
def add(message,session,match):
    user=message.source
    ch=match.group(1)
    if ch not in CHANNEL:
        return "该频道不存在！"
    client.tag_users(str(CHANNEL_ID[ch]),[user])
    return "订阅成功"

@robot.filter(re.compile("退订 (.*)"))
def dele(message,session,match):
    user=message.source
    ch=match.group(1)
    if ch not in CHANNEL:
        return "该频道不存在！"
    client.untag_users(CHANNEL_ID[ch],[user])
    return "退订成功"

@robot.filter("about")
def about(message,session,match):
    return "njuhelper-x by TomatoWang"

@robot.filter("列表")
def list(message,session,match):
    return "【频道列表】\n"+"\n".join(CHANNEL)

@robot.subscribe
def subscribe(message):
    return "欢迎使用南哪小帮手！\n订阅 [频道名称] 订阅一个频道\n退订 [频道名称] 退订一个频道\n列表 给出频道列表"
logger.success("robot ready")
logger.info("setting up rss ...")
rss_sources=[]
for i in CHANNEL:
    rss_sources.append(rss_source.RSS_Source({"name":i,"url":CHANNEL_URL[i],"id":CHANNEL_ID[i]}))
for i in rss_sources:
    i.bind(robot)
    i.run()
    logger.success("rss source:"+i.name+" ready")
logger.success("rss ready")

logger.info("all done, starting robot...")

robot.run(server='tornado')
