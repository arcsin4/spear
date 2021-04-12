# -*- coding: utf-8 -*-
import time
import datetime
import re
import json
import random

from requests.api import head

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl
from bs4 import BeautifulSoup

class CrawlSseinfo(BaseCrawl):

    _item_data_store = None

    _headers = {
        'Referer': 'http://sns.sseinfo.com/qa.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'sns.sseinfo.com',
        'Connection': 'close',
    }

    #_proxies_list = ["http://139.196.154.197:8080", "http://171.35.150.103:9999", "http://39.106.223.134:80",]
    _proxies_list = ["http://39.106.223.134:80",]
    _proxies_url = None

    _url = 'http://sns.sseinfo.com/ajax/feeds.do?type=11&pageSize={}&lastid=-1&show=1&page={}&_={}'
    _pagesize = 100

    _jumpurl = 'http://sns.sseinfo.com/qa.do'
    _website = 'sseinfo'

    _pids = None

    _time_res = {
        'seconds': re.compile('(\d+)秒前'),
        'minutes': re.compile('(\d+)分钟前'),
        'hours': re.compile('(\d+)小时前'),
        'yesterday': re.compile('昨天 ([\d\:]+)'),
        'md': re.compile('([\d\:\s月日]+)'),
    }

    _firstrun = True

    def __init__(self):

        super(CrawlSseinfo, self).__init__()

    def _run(self, page):
        url = self._url.format(self._pagesize, page, str(int(time.time()*1000)))

        if self._proxies_url is None:
            self._proxies_url = random.choice(self._proxies_list)

        proxies = {
            "http": self._proxies_url,
            "https": self._proxies_url,
        }

        status_code, response = self.get(url=url, get_params={}, proxies=proxies)

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {} use proxy: {}'.format(self._website, status_code, url, self._proxies_url))

            self.parseData(response)
        else:
            system_log.error('{} runCrawl failed [{}] {} use proxy: {}'.format(self._website, status_code, url, self._proxies_url))

    def run(self):

        if self._firstrun:
            system_log.info('{} first run'.format(self._website))
            for page in range(1, 10):
                self._run(page)
                time.sleep(1)

            self._firstrun = False
        else:
            self._run(1)

    def _parsetime(self, timestr):
        rr = re.fullmatch('(\d+)秒前', timestr, flags = 0)
        if rr is not None:
            d = int(rr.groups()[0])
            return datetime.datetime.now() + datetime.timedelta(seconds=-d)

        rr = re.fullmatch('(\d+)分钟前', timestr, flags = 0)
        if rr is not None:
            d = int(rr.groups()[0])
            return datetime.datetime.now() + datetime.timedelta(minutes=-d)

        rr = re.fullmatch('(\d+)小时前', timestr, flags = 0)
        if rr is not None:
            d = int(rr.groups()[0])
            return datetime.datetime.now() + datetime.timedelta(hours=-d)

        rr = re.fullmatch('昨天 ([\d\:]+)', timestr, flags = 0)
        if rr is not None:
            s = str(rr.groups()[0])

            x = datetime.datetime.now()+datetime.timedelta(days=-1)
            x2 = str(x.year)+'-'+str(x.month)+'-'+str(x.day)+' '+s

            return datetime.datetime.strptime(x2, '%Y-%m-%d %H:%M')

        rr = re.fullmatch('(\d+)天前', timestr, flags = 0)
        if rr is not None:
            d = int(rr.groups()[0])
            return datetime.datetime.now() + datetime.timedelta(days=-d)

        rr = re.fullmatch('([\d\:\s月日]+)', timestr, flags = 0)
        if rr is not None:
            s = str(rr.groups()[0])
            s = str(datetime.date.today().year)+'年'+s
            rtn = datetime.datetime.strptime(s, '%Y年%m月%d日 %H:%M')
            if rtn - datetime.datetime.now() > datetime.timedelta(days=1):
                rtn = rtn.replace(year = datetime.date.today().year-1)
            return rtn

        rr = re.fullmatch('([\d\:\s年月日]+)', timestr, flags = 0)
        if rr is not None:
            s = str(rr.groups()[0])
            return datetime.datetime.strptime(s, '%Y年%m月%d日 %H:%M')

        return None

    def parseData(self, response):

        soup = BeautifulSoup(response , 'lxml')

        datas = []

        for e in soup.find_all(class_='m_feed_item'):

            pid = str(e.attrs['id'].split('-')[1])

            if self._chkPidExist(pid):
                break

            title = e.find(class_='m_feed_detail m_qa_detail').find(class_='m_feed_txt').get_text(separator=' ', strip=True).strip(' :')
            content = e.find(class_='m_feed_detail m_qa').find(class_='m_feed_txt').get_text(separator=' ', strip=True).strip()
            timestr = e.find(class_='m_feed_detail m_qa').find(class_='m_feed_from').find(name='span').get_text(separator=' ', strip=True).strip()

            jumpurl = self._jumpurl

            news_time = self._parsetime(timestr)
            if news_time is not None:
                news_time = int(time.mktime(news_time.timetuple()))
            else:
                news_time = int(time.time())

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
