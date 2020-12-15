# -*- coding: utf-8 -*-
import yaml
import os
import copy

class Environment(object):

    _conf_dir = None
    _env_conf = None
    _crawl_conf = None

    _crawler_status = None
    _crawler_status_frame = {
        'last_run': 0,
        'run_counts': 0,
        'freq': [],
        'trigger': True,
        'trigger_part': [],
    }

    _event_keywords = None
    _websites = None

    _threads = None
    _notify_task_queue = None
    _monitor_task_queue = None
    _trigger_task_queue = None

    def __init__(self):

        self._crawler_status = {}
        pass

    @property
    def conf_dir(self):
        return self._conf_dir

    @property
    def log_dir(self):
        return os.path.abspath(os.path.join(self._conf_dir,os.path.pardir,'log'))

    @property
    def env_conf(self):
        if self._env_conf is None:
            self.loadEnvCfg()
        return self._env_conf

    @property
    def crawl_conf(self):
        if self._crawl_conf is None:
            self.loadCrawlCfg()
        return self._crawl_conf

    @property
    def crawler_status(self):
        return self._crawler_status

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

    def loadEnvCfg(self):

        self._env_conf = {}
        with open(self._conf_dir + '/env.yaml', 'r') as f:
            self._env_conf = yaml.load(f.read(), Loader=yaml.FullLoader)

    def loadCrawlCfg(self):

        self._crawl_conf = {}
        with open(self._conf_dir + '/crawl.yaml', 'r') as f:
            self._crawl_conf = yaml.load(f.read(), Loader=yaml.FullLoader)

    def registCrawler(self, crawler_name, freq=[10, 15], trigger=True, trigger_part=[]):
        self._crawler_status[crawler_name] = copy.deepcopy(self._crawler_status_frame)

        self._crawler_status[crawler_name]['freq'] = freq
        self._crawler_status[crawler_name]['trigger'] = trigger
        self._crawler_status[crawler_name]['trigger_part'] = trigger_part

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
