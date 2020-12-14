# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.item_data_store import ItemDataStore
from core.event.event_trigger import event_trigger
from core.crawler.base_crawl_request import BaseCrawlRequest

class CrawlCnstock(BaseCrawlRequest):

    _item_data_store = None

    _headers = {
            'Referer': 'http://app.cnstock.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'app.cnstock.com',

    }

    _url = 'https://app.cnstock.com/api/waterfall?callback=jQuery_{}&colunm=qmt-sns_bwkx&page={}&num={}&showstock=1&_={}'

    _pagesize = 100

    _website = 'cnstock'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlCnstock, self).__init__()
        self._item_data_store = ItemDataStore()

        res = self._item_data_store.getCrawlResults(website=self._website, limit=100)
        self._pids = set([str(r['pid']) for r in res])

    def _run(self, page):
        time_str = str(int(time.time()*1000))
        url = self._url.format(time_str, page, self._pagesize, time_str)

        status_code, response = self.post(url=url, post_data={})

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            self.parseData(response)
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

    def run(self):

        if self._firstrun:
            system_log.info('cnstock first run')

            for page in range(1, 10):
                self._run(page)
                time.sleep(1)

            self._firstrun = False
        else:
            self._run(1)

    def parseData(self, response):

        response = response[21:-1]

        m = json.loads(response)

        datas = []
        for l in m['data']['item']:

            pid = str(l['id'])

            if pid in self._pids:
                break


            title = l['title']
            content =  l['desc']
            jumpurl = l['link']
            news_time = int(time.mktime(time.strptime(l['time'], "%Y-%m-%d %H:%M:%S")))

            d = [self._website, pid, title, content, jumpurl, news_time, int(time.time())]

            env.trigger_task_queue.put(json.dumps(d))

            datas.append(d)
            #jQuery19109227179718174181_1606805973845({"msg":"success","code":"200","data":{"date":"2020-12-01","item":[{"id":"479b18268cf7ebc6d35be56f83bb42b1","title":"\u5c71\u897f\u7528\u7535\u529b\u5927\u6570\u636e\u201c\u4fa6\u5bdf\u201d\u4f01\u4e1a\u6392\u6c61","subtitle":"&nbsp;","link":"https:\/\/news.cnstock.com\/news,bwkx-202012-4625053.htm","desc":"\u3010\u5c71\u897f\u7528\u7535\u529b\u5927\u6570\u636e\u201c\u4fa6\u5bdf\u201d\u4f01\u4e1a\u6392\u6c61\u3011\u636e\u65b0\u534e\u793e\u592a\u539f12\u67081\u65e5\u7535\uff0c\u4e0d\u4e45\u524d\uff0c\u5728\u5c71\u897f\u7701\u91cd\u6c61\u67d3\u5929\u6c14\u6a59\u8272\u9884\u8b66\u671f\u95f4\uff0c\u592a\u539f\u5e02\u4e00\u5bb6\u6c34\u6ce5\u751f\u4ea7\u4f01\u4e1a\u88ab\u8981\u6c42\u9650\u4ea750%\u3002\u8fd9\u5bb6\u4f01\u4e1a\u767d\u5929\u6309\u73af\u4fdd\u90e8\u95e8\u8981\u6c42\u6267\u884c\uff0c22\u65f6\u540e\u5c31\u5f00\u8db3\u9a6c\u529b\u751f\u4ea7\u3002\u4ee4\u4f01\u4e1a\u6ca1\u60f3\u5230\u7684\u662f\uff0c\u5f53\u5929\u665a\u4e0a\u73af\u4fdd\u90e8\u95e8\u5de5\u4f5c\u4eba\u5458\u5c31\u4e0a\u95e8\u67e5\u5904\u3002","time":"2020-12-01 15:46:35","dateline":"2020\u5e7412\u670801\u65e5 15:46","i":"","color":"","keyword":["\u7535\u529b\u5927\u6570\u636e"],"stock":null,"isHot":"0","isCover":"0","typeId":"001","typeName":"\u666e\u901a","mp4":"","imgArr":[],"channel":"\u8981\u95fb","channelurl":"https:\/\/news.cnstock.com"}],"column":{"code":"sns_bwkx","name":"\u672c\u7f51\u5feb\u8baf"}}})

        if len(datas) > 0:
            #['website','pid','title','content','url','news_time','create_time']
            self._item_data_store.saveCrawlResults(data = datas)

            for x in datas:
                self._pids.add(x[1])
