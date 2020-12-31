# -*- coding: utf-8 -*-

from core.env import env
from core.logger import system_log

class EventTrigger(object):

    def __init__(self):
        pass

    def runTrigger(self, *k, website):
        res = set()
        for text in k:
            for kw in env.getEventKeywords(website=website):
                if kw.lower() in text.lower():
                    res.add(kw)

        return list(res)

event_trigger = EventTrigger()
