# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.item_data_store import ItemDataStore
from core.crawler.base_crawl_request import BaseCrawlRequest

from bs4 import BeautifulSoup

from urllib.parse import urljoin

class CrawlCs(BaseCrawlRequest):

    _item_data_store = None

    _headers = {
        'Referer': 'http://www.cs.com.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'www.cs.com.cn',
    }

    _url = 'http://www.cs.com.cn/sylm/jsbd/'

    _website = 'cs'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlCs, self).__init__()

        self._item_data_store = ItemDataStore()

        self.refreshPids()

    def refreshPids(self):

        res = self._item_data_store.getCrawlResults(website=self._website, limit=100)
        self._pids = set([str(r['pid']) for r in res])

    def _chkPidExist(self, pid):
        return str(pid) in self._pids

    def _addPid(self, pid):
        self._pids.add(str(pid))

    def _run(self):
        url = self._url

        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            self.parseData(response)
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

    def run(self):

        self._run()

    def parseData(self, response):

        soup = BeautifulSoup(response , 'lxml')

        datas = []

        for e in soup.find(class_='ch_type3_list').find_all(name='li'):

            pid = e.find(name='a').attrs['href']
            pid = pid.split('/')[-1]
            pid = pid.split('.')[0]

            if self._chkPidExist(pid):
                break

            #<li class="item"><a href="./202012/t20201201_6116434.html" target="_blank"><div><em>2020-12-01 18:59</em></div><h3>南风股份：中标5870万元项目</h3><span></span></a></li>

            news_time = int(time.mktime(time.strptime(e.find(name='em').get_text(separator=' ', strip=True).strip(), "%Y-%m-%d %H:%M")))
            title = e.find(name='h3').get_text(separator=' ', strip=True).strip()

            jumpurl = urljoin(self._url, e.find(name='a').attrs['href'])
            content = self._parseDataDetail(jumpurl)

            d = [self._website, pid, title, content, jumpurl, news_time, int(time.time())]

            env.trigger_task_queue.put(json.dumps(d))

            datas.append(d)

        if len(datas) > 0:
            #['website','pid','title','content','url','news_time','create_time']
            self._item_data_store.saveCrawlResults(data = datas)

            for x in datas:
                self._addPid(x[1])

    def _parseDataDetail(self, url):

        content = None
        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            soup_detail = BeautifulSoup(response , 'lxml')

            content = '<br />'.join([x.get_text(separator=' ', strip=True).strip() for x in soup_detail.find(name='article').find(name='section').find_all(name='p')])
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

        return content
