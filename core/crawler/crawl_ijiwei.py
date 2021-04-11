# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl

class CrawlIjiwei(BaseCrawl):

    _item_data_store = None

    _headers = {
        'Referer': 'https://www.ijiwei.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'ijiwei.com',
        'Connection': 'close',
    }

    _url = 'https://www.ijiwei.com/api/news/feedstream'

    _website = 'ijiwei'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlIjiwei, self).__init__()

    def _run(self, essence_level=4, limit=16, after=0):
        url = self._url

        post_data = {
            'essence_level': essence_level,
            'limit': limit,
            'source': 'pc',
            'token': '',
            'timestamp': int(time.time()*1000),
        }

        if after > 0:
            post_data['after'] = after

        status_code, response = self.post(url=url, post_data=post_data, headers=self._headers)

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            return self.parseData(response, next=True)
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

    def run(self):

        self._run(essence_level=4, limit=16, after=0)
        self._run(essence_level=3, limit=100, after=0)

        # if self._firstrun:
        #     system_log.info('{} first run'.format(self._website))

        #     page_callback = self._run(page_callback)
        #     time.sleep(1)
        #     self._firstrun = False

    def parseData(self, response, next = False):

        res = json.loads(response)

        item_list = res['data']

        datas = []
        for item in item_list:
            pid = str(item['news_id'])

            if self._chkPidExist(pid):
                break

            title = item['news_title']
            content = item['intro']
            news_time = int(time.mktime(time.strptime(item['published_time'], "%Y%m%d%H%M%S")))

            jumpurl = item['share_url']

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
