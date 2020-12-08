# -*- coding: utf-8 -*-
import yaml

class Environment(object):

    _conf_dir = None
    _env_conf = None
    _crawl_conf = None

    _event_keywords = None
    _websites = None

    _threads = None
    _notify_task_queue = None
    _monitor_task_queue = None
    _trigger_task_queue = None

    def __init__(self):
        pass

    @property
    def conf_dir(self):
        return self._conf_dir


    @property
    def env_conf(self):
        return self._env_conf

    @property
    def crawl_conf(self):
        return self._crawl_conf

    @property
    def event_keywords(self):
        return self._event_keywords

    @property
    def websites(self):
        return self._websites

    @property
    def threads(self):
        return self._threads

    @property
    def notify_task_queue(self):
        return self._notify_task_queue

    @property
    def monitor_task_queue(self):
        return self._monitor_task_queue

    @property
    def trigger_task_queue(self):
        return self._trigger_task_queue

    def setConfDir(self, conf_dir:str):

        self._conf_dir = conf_dir

        self._env_conf = {}
        with open(self._conf_dir + '/env.yaml', 'r') as f:
            self._env_conf = yaml.load(f.read(), Loader=yaml.FullLoader)

        self._crawl_conf = {}
        with open(self._conf_dir + '/crawl.yaml', 'r') as f:
            self._crawl_conf = yaml.load(f.read(), Loader=yaml.FullLoader)

    def setEventKeywords(self, event_keywords):
        self._event_keywords = event_keywords

    def setWebsites(self, websites):
        self._websites = websites

    def setNofityTaskQueue(self, tq):
        self._notify_task_queue = tq

    def setMonitorTaskQueue(self, tq):
        self._monitor_task_queue = tq

    def setTriggerTaskQueue(self, tq):
        self._trigger_task_queue = tq

    def setThreads(self, threads):
        self._threads = threads

env = Environment()
