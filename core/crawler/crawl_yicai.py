# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.base_crawl import BaseCrawl

from urllib.parse import urljoin

class CrawlYicai(BaseCrawl):

    _item_data_store = None

    _headers = {
        'Referer': 'https://www.yicai.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Host': 'www.yicai.com',
        'Connection': 'close',

    }

    _url = 'https://www.yicai.com/api/ajax/getlatest?page={}&pagesize={}'

    _url_detail = 'https://www.yicai.com/'

    _pagesize = 50

    _website = 'yicai'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlYicai, self).__init__()

    def _run(self, page):
        url = self._url.format(page, self._pagesize)

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

        m = json.loads(response)

        datas = []
        for l in m:

            pid = str(l['NewsID'])

            if self._chkPidExist(pid):
                break


            title = l['NewsTitle']
            content =  l['NewsNotes']
            jumpurl = urljoin(self._url_detail, l['url'])

            news_time = int(time.mktime(time.strptime(l['CreateDate'], "%Y-%m-%dT%H:%M:%S")))

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

        # [{"ChainType":false,"ChannelID":54,"ChannelName":"A股","CreateDate":"2020-12-16T10:45:12","CreaterName":"李志","EntityChannel":0,"EntityName":"","EntityNews":0,"EntityPath":"","IsEntity":true,"LastDate":"2020-12-16T10:44:22","LiveDate":null,"LiveState":0,"NewsAddons":"","NewsAuthor":"一财资讯","NewsHot":0,"NewsID":100878842,"NewsLength":957,"NewsNotes":"此前有报道称，苹果将iPhone明年上半年的产量提升30%，也就是从2021年1月至6月将iPhone产量增加至9600万部。","NewsSource":"第一财经","NewsThumbs":"2020/12/ad0857221f0fa740f8a826fa975daef9.jpg","NewsTitle":"iPhone扩产 果链概念股应声反弹 机构：仍处上行周期丨牛熊眼","NewsType":10,"NewsUrl":"","OuterUrl":"","SpeechAddress":"","SpeechLength":0,"SubChannelID":0,"SubChannelName":"","Tags":"","UniqueTag":0,"VideoSource":"","VideoUrl":"","VideoUrl4k":"","VideoUrl8k":"","VideoUrlFhd":"","VideoUrlHd":"","VideoUrlOrignal":"","isTextToSpeech":false,"topics":"","originPic":"//imgcdn.yicai.com/uppics/slides/2020/12/ad0857221f0fa740f8a826fa975daef9.jpg","pubDate":"31分钟前","showDate":"31分钟前","NewsAuthor1":["一财资讯"],"url":"/news/100878842.html","thumbsType":1},]