# -*- coding: utf-8 -*-
import time
import datetime

from core.env import env
from core.logger import system_log

from core.event.notify_dingding import NotifyDingding

class EventTrigger(object):

    def __init__(self):
        pass

    def runTrigger(self, *k):
        res = set()
        for text in k:
            for kw in env.event_keywords:
                if kw.lower() in text.lower():
                    res.add(kw)

        return list(res)

    def runNotify(self, head_kws, title, content, origin='', jump_url='', news_time=0, **kw):
        now_time = time.time()
        if int(news_time) - time.time() > 86400:
            system_log.debug('runNotify msg droped news_time:{} now_time:{}'.format(news_time, now_time))
            return False

        timestr = datetime.datetime.fromtimestamp(news_time).strftime('%m-%d %H:%M:%S')
        return NotifyDingding.notify(head_kws=head_kws, title=title, content=content, origin=origin, jump_url=jump_url, timestr=timestr)

event_trigger = EventTrigger()
