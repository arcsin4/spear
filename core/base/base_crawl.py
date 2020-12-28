# -*- coding: utf-8 -*-
import re
import datetime

from core.logger import system_log
from core.base.item_data_store import ItemDataStore
from core.base.base_crawl_request import BaseCrawlRequest

class BaseCrawl(BaseCrawlRequest):

    _item_data_store = None

    _website = ''

    _pids = None

    def __init__(self):
        super(BaseCrawl, self).__init__()

        self._item_data_store = ItemDataStore()

        self.refreshPids()

    def refreshPids(self):

        res = self._item_data_store.getCrawlResults(website=self._website, limit=1000)
        self._pids = set([str(r['pid']) for r in res])

    def _chkPidExist(self, pid):
        return str(pid) in self._pids

    def _addPid(self, pid):
        self._pids.add(str(pid))

    def run(self):
        raise NotImplementedError('No such method {}'.format('run'))

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
