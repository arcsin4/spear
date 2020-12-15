# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.item_data_store import ItemDataStore
from core.crawler.base_crawl_request import BaseCrawlRequest
from bs4 import BeautifulSoup

class Crawl36kr(BaseCrawlRequest):

    _item_data_store = None

    _headers = {
            'Referer': 'https://36kr.com/newsflashes',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': '36kr.com',
    }

    _headers_next = {
            'Referer': 'https://36kr.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'content-type': 'application/json',
    }

    _url = 'https://36kr.com/newsflashes'
    _url_next = 'https://gateway.36kr.com/api/mis/nav/newsflash/flow'

    _jumpurl = 'https://36kr.com/newsflashes/{}'
    _website = '36kr'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(Crawl36kr, self).__init__()

        self._item_data_store = ItemDataStore()

        self.refreshPids()

    def refreshPids(self):

        res = self._item_data_store.getCrawlResults(website=self._website, limit=100)
        self._pids = set([str(r['pid']) for r in res])

    def _chkPidExist(self, pid):
        return str(pid) in self._pids

    def _addPid(self, pid):
        self._pids.add(str(pid))

    def _runNext(self, page_callback):
        url = self._url

        post_data = {
            'param': {
                'pageEvent': 1,
                'pageSize': 1000,
                'pageCallback': page_callback,
                'platformId': 2,
                'siteId': 1,
            },
            'partner_id': "web",
            'timestamp': int(time.time()*1000),
        }

        status_code, response = self.post(url=self._url_next, post_data=json.dumps(post_data), headers=self._headers_next)

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            return self.parseData(response, next=True)
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

    def _run(self):
        url = self._url

        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            return self.parseData(response)
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

    def run(self):

        page_callback = self._run()

        if self._firstrun:
            system_log.info('{} first run'.format(self._website))

            page_callback = self._runNext(page_callback)
            time.sleep(1)
            self._firstrun = False

    def parseData(self, response, next = False):

        if not next:
            soup = BeautifulSoup(response , 'lxml')

            res = soup.body.find(name='script').string.strip()
            res = res[res.find('{'):]
            res = json.loads(res)

            page_callback = res['newsflashCatalogData']['data']['newsflashList']['data']['pageCallback']
            has_nextpage = res['newsflashCatalogData']['data']['newsflashList']['data']['hasNextPage']

            item_list = res['newsflashCatalogData']['data']['newsflashList']['data']['itemList']

        else:
            res = json.loads(response)

            page_callback = res['data']['pageCallback']
            has_nextpage = res['data']['hasNextPage']

            item_list = res['data']['itemList']

        datas = []
        for item in item_list:
            pid = str(item['itemId'])

            if self._chkPidExist(pid):
                break

            title = item['templateMaterial']['widgetTitle']
            content = item['templateMaterial']['widgetContent']
            news_time = int(item['templateMaterial']['publishTime'])//1000

            jumpurl = self._jumpurl.format(pid)

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

        if int(has_nextpage) >= 1 and len(page_callback) > 0:
            return page_callback

        return ''
