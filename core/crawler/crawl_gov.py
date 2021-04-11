# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl

from bs4 import BeautifulSoup

from urllib.parse import urljoin

class CrawlGov(BaseCrawl):

    _item_data_store = None

    _headers = {
        'Referer': 'http://sousuo.gov.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'sousuo.gov.cn',
        'Connection': 'close',
    }

    _headers_detail = {
        'Referer': 'http://www.gov.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'www.gov.cn',
        'Connection': 'close',
    }

    _url = 'http://sousuo.gov.cn/column/30611/{}.htm'

    _website = 'gov'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlGov, self).__init__()

    def _run(self, page):
        url = self._url.format(page)

        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            self.parseData(response)
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

    def run(self):

        if self._firstrun:
            system_log.info('{} first run'.format(self._website))

            for page in range(0, 10):
                self._run(page)
                time.sleep(1)

            self._firstrun = False
        else:
            self._run(0)

    def parseData(self, response):

        soup = BeautifulSoup(response , 'lxml')

        datas = []

        for e in soup.find(class_='listTxt').find_all(name='h4'):

            jumpurl = e.find(name='a').attrs['href']

            pid = '/'.join(jumpurl.split('/')[4:])
            pid = pid.split('.')[0]

            if self._chkPidExist(pid):
                break

            #<a href="http://www.gov.cn/xinwen/2020-12/16/content_5569798.htm" target="_blank">150部珍贵古籍在重庆展出</a>
            title = e.find(name='a').get_text(separator=' ', strip=True).strip()
            timestr = e.find(name='span').get_text(separator=' ', strip=True).strip()

            news_time = self._parsetime(timestr)

            if news_time is not None:
                news_time = int(time.mktime(news_time.timetuple()))
            else:
                news_time = int(time.time())

            timestr, content = self._parseDataDetail(jumpurl)

            if timestr is not None and len(timestr) > 0:
                news_time = int(time.mktime(time.strptime(timestr, "%Y-%m-%d %H:%M")))

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

    def _parseDataDetail(self, url):

        timestr = None
        content = ''
        status_code, response = self.get(url=url, get_params={}, headers=self._headers_detail)

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            try:
                soup_detail = BeautifulSoup(response , 'lxml')

                content = '<br />'.join([x.get_text(separator=' ', strip=True).strip() for x in soup_detail.find(class_='pages_content').find_all(name='p')])

                timestr = list(soup_detail.find(class_='pages-date').stripped_strings)[0].strip()

            except Exception as ex:
                pass
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

        return timestr, content
