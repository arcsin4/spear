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

        now_datetime = datetime.datetime.now()

        notify_start = 9
        notify_end = 15

        try:
            notify_start = env.env_conf['trigger_notify_period']['value'][0]
            notify_end = env.env_conf['trigger_notify_period']['value'][1]
        except Exception as ex:
            system_log.error("get env_conf trigger_notify_period failed {}".format(env.env_conf))
            pass

        if int(now_datetime.hour) < notify_start or int(now_datetime.hour) > notify_end:
            return

        now_time = time.time()

        expired_seconds = 3600

        try:
            if int(env.env_conf['trigger_msg_expired']['value']) > 0:
                expired_seconds = int(env.env_conf['trigger_msg_expired']['value'])
        except Exception as ex:
            system_log.error("get env_conf trigger_msg_expired failed {}".format(env.env_conf))
            pass

        if int(news_time) - time.time() > expired_seconds:
            system_log.debug('runNotify msg droped news_time:{} now_time:{}'.format(news_time, now_time))
            return False

        timestr = datetime.datetime.fromtimestamp(news_time).strftime('%m-%d %H:%M:%S')
        return NotifyDingding.notify(head_kws=head_kws, title=title, content=content, origin=origin, jump_url=jump_url, timestr=timestr)

event_trigger = EventTrigger()
