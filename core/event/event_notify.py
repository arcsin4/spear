# -*- coding: utf-8 -*-
import time
import datetime

from core.env import env
from core.logger import system_log

from core.event import NOTIFIERS

class EventNotify(object):

    _notifiers = None

    def __init__(self):

        self._notifiers = NOTIFIERS

    def runNotify(self, head_kws, title, content, origin='', jump_url='', news_time=0, **kw):

        now_datetime = datetime.datetime.now()

        if now_datetime.weekday() >= 5:
            return

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

        if (time.time() - int(news_time))  > expired_seconds:
            system_log.debug('runNotify msg droped news_time:{} now_time:{}'.format(news_time, now_time))
            return False

        timestr = datetime.datetime.fromtimestamp(news_time).strftime('%m-%d %H:%M:%S')

        for _, notifier in self._notifiers.items():
            notifier.notify(head_kws=head_kws, title=title, content=content, origin=origin, jump_url=jump_url, timestr=timestr)

event_notify = EventNotify()
