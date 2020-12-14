# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.item_data_store import ItemDataStore
from core.crawler.base_crawl_request import BaseCrawlRequest

class CrawlCninfo(BaseCrawlRequest):

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

        self._item_data_store = ItemDataStore()

        self.refreshPids()

    def refreshPids(self):

        res = self._item_data_store.getCrawlResults(website=self._website, limit=100)
        self._pids = set([str(r['pid']) for r in res])

    def _chkPidExist(self, pid):
        return str(pid) in self._pids

    def _addPid(self, pid):
        self._pids.add(str(pid))

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
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            self.parseData(response)
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

    def run(self):

        if self._firstrun:
            system_log.info('cninfo first run')

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

            d = [self._website, pid, title, content, jumpurl, news_time, int(time.time())]

            env.trigger_task_queue.put(json.dumps(d))

            datas.append(d)

            #{'esId': '11_786292636349841408', 'indexId': '786292636349841408', 'contentType': 11, 'trade': ['制造业'], 'mainContent': '董秘您好，从公司公告（编号：2020-071）知悉，贵公司2020年10月30日就已经收到了一次反馈意见通知书（202771号），从其他公开渠道可以查询到，其他发行可转债的上市公司，都在收到证监会的反馈意见通知书后及时做了公告披露。请问贵公司为何在1个月后的11月24日直至回复时才予以披露，请问该收到反馈意见通知书事项是选择性披露事项吗？在形成反馈意见的一个月时间内，公司股价较大波动，是否有影响。', 'stockCode': '002126', 'secid': '9900002661', 'companyShortName': '银轮股份', 'companyLogo': 'S002126/images/002126.gif', 'boardType': ['012003'], 'pubDate': '1606272510000', 'updateDate': '1606803459000', 'author': '91929087014076416', 'authorName': '有想法', 'pubClient': '6', 'attachedId': '790853453530644480', 'attachedContent': '您好！公司根据相关规定，在30天内提交书面回复意见并公告。详见公司于2020年11月25日刊登在指定媒体的《关于公开发行可转换公司债券申请文件反馈意见回复的公告》（编号：2020-071）、《浙江银轮机械股份有限公司公开发行可转换公司债券申请文件反馈意见的回复》。披露符合规则要求。', 'attachedAuthor': '银轮股份', 'attachedPubDate': '1606803459000', 'score': 0.0, 'topStatus': 0, 'praiseCount': 0, 'praiseStatus': False, 'favoriteStatus': False, 'attentionCompany': False, 'isCheck': '1', 'qaStatus': 2, 'packageDate': '14分钟前'}

        if len(datas) > 0:
            #['website','pid','title','content','url','news_time','create_time']
            self._item_data_store.saveCrawlResults(data = datas)

            for x in datas:
                self._addPid(x[1])
