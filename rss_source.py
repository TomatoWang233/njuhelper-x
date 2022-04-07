from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.triggers.interval import IntervalTrigger  
from tornado import httpclient
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
    def update(self):
        response = await httpclient.AsyncHTTPClient().fetch(self.url).body.decode(encoding="utf-8")
        new_hash=hash(response)
        if self.hash != new_hash:
            # hash 不一致 RSS更新，准备群发
            new_entries=feedparser.parse(response).entries
            # post 要投递的 RSS 信息
            post=[i for i in new_entries if i not in self.entries]
            self.entries=new_entries
            self.hash=new_hash
            usr_list=self.bot.cilent.get_users_by_tag(str(self.id))
            for usr in usr_list:
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
                        "value": "订阅"
                    },
                    "keyword3": {
                        "value": i["summary"]
                    },
                    "keyword4": {
                        "value": "南哪小助手"
                    },
                    "keyword5": {
                        "value": "title"
                    },
                    "remark": {
                        "value": "测试模板消息"
                    },
                }
                    self.bot.client.send_template_message(usr,TEMPLATE,data,url="www.baidu.com")
                pass
        pass
    def run(self):
        scheduler.add_job(self.update,trigger=IntervalTrigger(minutes=10,jitter=10))
        pass
    def bind(self,bot):
        self.bot=bot
        