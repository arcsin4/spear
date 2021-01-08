# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl

from bs4 import BeautifulSoup

from urllib.parse import urljoin

class CrawlThepaper(BaseCrawl):

    _item_data_store = None

    _headers = {
        'Referer': 'https://www.thepaper.cn/list_25434',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'www.thepaper.cn',
    }

    _url = 'https://www.thepaper.cn/list_25434'
    _url_next = 'https://www.thepaper.cn/load_index.jsp?nodeids=25434&topCids=&pageidx={}&isList=true&lastTime={}'

    _url_jump = 'https://www.thepaper.cn/'

    _website = 'thepaper'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlThepaper, self).__init__()

    def _run(self, url):

        status_code, response = self.post(url=url, post_data={})

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            self.parseData(response)
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

    def run(self):

        if self._firstrun:
            system_log.info('{} first run'.format(self._website))

            self._run(self._url)
            time.sleep(1)

            for page in range(2, 10):
                self._run(self._url_next.format(page, str(int(time.time()*1000))))
                time.sleep(1)

            self._firstrun = False
        else:
            self._run(self._url)

    def parseData(self, response):

        soup = BeautifulSoup(response , 'lxml')

        datas = []

        try:
            el = soup.find(id='indexScroll').find_all(class_='news_li')
        except Exception as ex:
            el = soup.find_all(class_='news_li')

        for e in el:

            try:
                pid = e.find(name='h2').find(name='a').attrs['id']
            except Exception as ex:
                continue

            if self._chkPidExist(pid):
                break

            title = e.find(name='h2').find(name='a').get_text(separator=' ', strip=True).strip()
            timestr = e.find(class_='pdtt_trbs').find(name='span').get_text(separator=' ', strip=True).strip()

            news_time = self._parsetime(timestr)
            if news_time is not None:
                news_time = int(time.mktime(news_time.timetuple()))
            else:
                news_time = int(time.time())

            jumpurl = urljoin(self._url_jump, e.find(name='h2').find(name='a').attrs['href'])

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

        timestr = ''
        content = ''
        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            try:
                soup_detail = BeautifulSoup(response , 'lxml')

                content = soup_detail.find(class_='news_txt').get_text(separator='<br />', strip=True).strip()

                timestr = list(soup_detail.find(class_='news_about').find_all(name='p')[1].stripped_strings)[0].strip()

            except Exception as ex:
                pass
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

        return timestr, content
