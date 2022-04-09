from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.triggers.interval import IntervalTrigger
from tornado import httpclient
from loguru import logger
import feedparser

global scheduler
scheduler=TornadoScheduler()
scheduler.start()
# CONFIG PART
global TEMPLATE
TEMPLATE=""
# ===
class RSS_Source:
    def __init__(self,param):
        self.name=param["name"]
        self.url=param["url"]
        self.id=param["id"]
        self.hash=0
        self.entries=[]
    async def update(self):
       logger.info("开始检查:"+self.name)
       response=await httpclient.AsyncHTTPClient().fetch(self.url)
       logger.info("检查完成:"+self.name)
       response=response.body.decode(encoding="utf-8")
       new_hash=hash(response)
       if self.hash != new_hash:
           logger.info("检查到更新:"+self.name)
           # hash 不一致 RSS更新，准备群发
           new_entries=feedparser.parse(response).entries
           # post 要投递的 RSS 信息
           post=[i for i in new_entries if i not in self.entries]
           self.entries=new_entries
           self.hash=new_hash
           usr_list=self.bot.client.get_users_by_tag(str(self.id))
           if usr_list["count"]==0:
               return
           for usr in usr_list["data"]["openid"]:
               for i in post:
                   # data 格式
                   data={
                    "first": {
                        "value": "订阅已更新"
                    },
                    "keyword1": {
                        "value": i["title"]
                    },
                    "keyword2": {
                        "value": self.name
                    },
                    "keyword3": {
                        "value":i["published"]  # "TIME HERE"
                    },
                    "keyword4": {
                        "value": "NJU"
                    },
                    "keyword5": {
                        "value": i["summary"]
                    },
                    "remark": {
                        "value": "Powered by njuhelper-x"
                    },
                      }
                   self.bot.client.send_template_message(usr,TEMPLATE,data,url=i["link"])
    def run(self):
        #预计最终版本是十分钟一更新
        scheduler.add_job(self.update,trigger=IntervalTrigger(minutes=10,jitter=10))
        pass
    def bind(self,bot):
        self.bot=bot
