# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl

from urllib.parse import urljoin

class CrawlCctv(BaseCrawl):

    _item_data_store = None

    _headers = {
            'Referer': 'https://news.cctv.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'news.cctv.com',

    }

    _url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_{}.jsonp?cb=news'

    _website = 'cctv'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlCctv, self).__init__()

    def _run(self, page):
        url = self._url.format(page)

        status_code, response = self.post(url=url, post_data={})

        if status_code == 200:
            system_log.debug('{} runCrawl success [{}] {}'.format(self._website, status_code, url))

            self.parseData(response)
        else:
            system_log.error('{} runCrawl failed [{}] {}'.format(self._website, status_code, url))

    def run(self):

        if self._firstrun:
            system_log.info('{} first run'.format(self._website))

            for page in range(1, 8):
                self._run(page)
                time.sleep(1)

            self._firstrun = False
        else:
            self._run(1)

    def parseData(self, response):

        response = response[5:-1]
        m = json.loads(response)

        datas = []
        for l in m['data']['list']:

            pid = str(l['id'])

            if self._chkPidExist(pid):
                break


            title = l['title']
            content =  l['brief']
            jumpurl = l['url']

            news_time = int(time.mktime(time.strptime(l['focus_date'], "%Y-%m-%d %H:%M:%S")))

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

        # news({"data":{"total":500,"list":[{"id":"PHOA04QlD982KLX4FmenJuR4201215","image2":"https://p5.img.cctvpic.com/photoworkspace/2020/12/15/2020121509380228731.jpg","title":"冬日星空","keywords":"冬日 星空 双子座 流星雨","count":"4","ext_field":"","image":"https://p5.img.cctvpic.com/photoworkspace/2020/12/15/2020121509380546849.jpg","focus_date":"2020-12-15 09:39:22","image3":"","brief":"这种特殊的流星雨被称为双子座流星雨，它的名字来源于双子座，因为流星似乎是从天空中的这个星座出发的。","url":"https://photo.cctv.com/2020/12/15/PHOA04QlD982KLX4FmenJuR4201215.shtml"},]}})