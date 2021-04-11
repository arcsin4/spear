# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl

class CrawlCnstock(BaseCrawl):

    _item_data_store = None

    _headers = {
        'Referer': 'https://news.cnstock.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'app.cnstock.com',
        'Connection': 'close',
    }

    _url = 'https://app.cnstock.com/api/waterfall?callback=jQuery_{}&colunm=qmt-sns_bwkx&page={}&num={}&showstock=1&_={}'

    _pagesize = 100

    _website = 'cnstock'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlCnstock, self).__init__()

    def _run(self, page):
        time_str = str(int(time.time()*1000))
        url = self._url.format(time_str, page, self._pagesize, time_str)

        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            self.parseData(response)
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

    def run(self):

        if self._firstrun:
            system_log.info('{} first run'.format(self._website))

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

            if self._chkPidExist(pid):
                break


            title = l['title']
            content =  l['desc']
            jumpurl = l['link']
            news_time = int(time.mktime(time.strptime(l['time'], "%Y-%m-%d %H:%M:%S")))

            d = {
                'website': self._website,
                'pid': pid,
                'title': title,
                'content': content,
                'url': jumpurl,
                'news_time': news_time,
                'create_time': int(time.time()),
            }
            #d = [self._website, pid, title, content, jumpurl, news_time, int(time.time())]

            env.trigger_task_queue.put(json.dumps(d))

            datas.append(d)

        if len(datas) > 0:
            #['website','pid','title','content','url','news_time','create_time']
            self._item_data_store.saveCrawlResults(data = datas)

            for x in datas:
                self._addPid(x['pid'])
