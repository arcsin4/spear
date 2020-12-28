# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl

class CrawlCninfo(BaseCrawl):

    _item_data_store = None

    _headers = {
            'Referer': 'http://irm.cninfo.com.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'irm.cninfo.com.cn',

    }

    _url = 'http://irm.cninfo.com.cn/ircs/index/search'

    _pagesize = 100

    _jumpurl = 'http://irm.cninfo.com.cn/ircs/question/questionDetail?questionId={}'

    _website = 'cninfo'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlCninfo, self).__init__()

    def _run(self, page):
        url = self._url

        post_data = {
            'pageNo': page,
            'pageSize': self._pagesize,
            'searchTypes': '11,',
            'market': '',
            'industry': '',
            'stockCode': '',
        }

        status_code, response = self.post(url=url, post_data=post_data)

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

        m = json.loads(response)

        datas = []
        for l in m['results']:
            pid = str(l['indexId'])

            if self._chkPidExist(pid):
                break

            title = l['companyShortName']+' ['+l['stockCode']+']: '+l['mainContent']
            content =  l['attachedContent']
            news_time = int(l['attachedPubDate'])//1000
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
