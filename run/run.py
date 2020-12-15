# -*- coding: utf-8 -*-

import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__),os.path.pardir,os.path.pardir))
CONF_DIR = os.path.join(BASE_DIR, 'conf')
sys.path.append(BASE_DIR) #把上级目录加入到变量中

from core.env import env
env.setConfDir(conf_dir = CONF_DIR)
env.loadEnvCfg()
env.loadCrawlCfg()

import traceback
import click
import threading
import queue
import time
import random
import json
import copy

import logbook
from core.logger import system_log

from core.crawler import *
from core.base.item_data_store import ItemDataStore
from core.event.event_trigger import event_trigger

item_data_store = ItemDataStore()
env.setEventKeywords(item_data_store.getEventKeywords())
env.setWebsites(item_data_store.getWebsites())

env.setNofityTaskQueue(queue.Queue(100000))
env.setMonitorTaskQueue(queue.Queue(100000))
env.setTriggerTaskQueue(queue.Queue(100000))

def threadCrawlWorker(**kw):
    system_log.info('crawl线程[{}] 启动'.format(threading.current_thread().name))

    crawlers = {}
    for crawl_website,crawl_website_conf in kw.items():
        freq = crawl_website_conf['freq']
        trigger = crawl_website_conf['trigger']
        trigger_part = crawl_website_conf['trigger_part']

        if freq is None or len(freq) <= 0:
            freq = [10, 15]
            try:
                if len(env.crawl_conf['default_crawl_freq']) > 0:
                    freq = env.crawl_conf['default_crawl_freq']
            except:
                pass

        env.registCrawler(crawl_website, freq=freq, trigger=trigger, trigger_part=trigger_part)

        crawlers[crawl_website] = eval(crawl_website_conf['class'])()

    while True:
        for crawl_website, cls in crawlers.items():

            if env.crawler_status[crawl_website]['last_run'] <= 0:
                system_log.debug('{} run last_run < 0'.format(crawl_website))
                pass
            else:
                if time.time() - env.crawler_status[crawl_website]['last_run'] <= env.crawler_status[crawl_website]['freq'][0]:
                    system_log.error('{} run to fast'.format(crawl_website))
                    continue

            try:
                cls.run()
                env.crawler_status[crawl_website]['last_run'] = time.time()
                env.crawler_status[crawl_website]['run_counts'] = env.crawler_status[crawl_website]['run_counts'] + 1
            except Exception as ex:
                system_log.error('crawl run error: {} {}'.format(ex, str(traceback.format_exc())))
                continue


        time.sleep(random.randint(3,5))

        monitor_msg = {
            'type':'alive',
            'thread_type': 'crawlers',
            'thread_name': threading.current_thread().name,
            'time': time.time(),
        }
        env.monitor_task_queue.put(json.dumps(monitor_msg))

def threadTriggerWorker():
    system_log.info('trigger线程[{}] 启动'.format(threading.current_thread().name))

    while True:
        try:
            try:
                msg = env.trigger_task_queue.get(timeout=1)
                system_log.debug('['+threading.current_thread().name+']: '+msg)

                msg_data = json.loads(msg)

                website = msg_data['website']

                if env.crawler_status[website]['trigger']:
                    pass
                else:
                    continue

                #website, pid, title, content, jumpurl, news_time, create_time = json.loads(msg)

                trigger_flag = False

                if len(env.crawler_status[website]['trigger_part']) > 0:
                    tp = [msg_data[x] for x in env.crawler_status[website]['trigger_part']]
                    head_kws = event_trigger.runTrigger(*tp)

                    if len(head_kws) > 0:
                        trigger_flag = True
                else:
                    head_kws = []
                    trigger_flag = True

                if trigger_flag:
                    origin = website
                    if website in env.websites.keys():
                        origin = env.websites[website]

                    notify_msg = {
                        'head_kws': head_kws,
                        'website': website,
                        'pid': msg_data['pid'],
                        'title': msg_data['title'],
                        'content': msg_data['content'],
                        'origin': origin,
                        'jump_url': msg_data['url'],
                        'news_time': msg_data['news_time'],
                    }
                    env.notify_task_queue.put(json.dumps(notify_msg))

                    #columns = ['website','pid', 'trigger_words', 'title','content', 'origin', 'jump_url','news_time','create_time']
                    item_data_store.saveTriggerMsg([notify_msg['website'], notify_msg['pid'], ','.join(notify_msg['head_kws']), notify_msg['title'], notify_msg['content'], notify_msg['origin'], notify_msg['jump_url'], notify_msg['news_time'], int(time.time()) ])

                #time.sleep(1)
            except queue.Empty as ex:
                continue
            except Exception as ex:
                system_log.error('get trigger task queue error:{}'.format(ex))
                #raise
            finally:
                pass
                #env.trigger_task_queue.task_done()
        except Exception as ex:
            system_log.error('operation trigger task queue error:{}'.format(ex))
            #raise

        monitor_msg = {
            'type':'alive',
            'thread_type': 'trigger',
            'thread_name': threading.current_thread().name,
            'time': time.time(),
        }
        env.monitor_task_queue.put(json.dumps(monitor_msg))

def threadNotifyWorker():
    system_log.info('notify线程[{}] 启动'.format(threading.current_thread().name))

    while True:
        try:
            try:
                msg = env.notify_task_queue.get(timeout=1)
                system_log.debug('['+threading.current_thread().name+']: '+msg)

                msg = json.loads(msg)

                event_trigger.runNotify(**msg)

                #time.sleep(1)
            except queue.Empty as ex:
                continue
            except Exception as ex:
                system_log.error('get notify task queue error:{}'.format(ex))
                #raise
            finally:
                pass
                #env.notify_task_queue.task_done()
        except Exception as ex:
            system_log.error('operation notify task queue error:{}'.format(ex))
            #raise

        monitor_msg = {
            'type':'alive',
            'thread_type': 'notifier',
            'thread_name': threading.current_thread().name,
            'time': time.time(),
        }
        env.monitor_task_queue.put(json.dumps(monitor_msg))

def threadMonitorWorker():
    system_log.info('monitor线程[{}] 启动'.format(threading.current_thread().name))

    while True:
        try:
            try:
                msg = env.monitor_task_queue.get()
                system_log.debug('['+threading.current_thread().name+']: '+msg)
                #time.sleep(1)
            except Exception as ex:
                system_log.error('get monitor task queue error:{}'.format(ex))
                #raise
            finally:
                pass
                #env.monitor_task_queue.task_done()
        except Exception as ex:
            system_log.error('operation monitor task queue error:{}'.format(ex))
            #raise

def threadEnvWorker():
    system_log.info('env线程[{}] 启动'.format(threading.current_thread().name))

    while True:
        try:
            env.setEventKeywords(item_data_store.getEventKeywords())
        except Exception as ex:
            system_log.error('refresh env error:{}'.format(ex))
            #raise

        monitor_msg = {
            'type':'alive',
            'thread_type': 'env',
            'thread_name': threading.current_thread().name,
            'time': time.time(),
        }
        env.monitor_task_queue.put(json.dumps(monitor_msg))

        system_log.error(env.crawler_status)

        time.sleep(30)

@click.group()
@click.help_option('-h', '--help')
def cli():
    '''执行爬虫程序'''
    pass

@cli.command()
@click.help_option('-h', '--help')
@click.option('-l', '--log-level', 'log_level', type=click.Choice(['debug', 'info', 'warning', 'error']), default='info', required=False, help='日志级别')
def runCrawl(log_level='info'):
    '''运行爬虫'''

    system_log.level = getattr(logbook, log_level.upper())

    threads = {'crawlers':{}, 'monitor':None, 'notifier':None, 'trigger':None, 'env':None}

    trigger_t = threading.Thread(target=threadTriggerWorker, name='trigger')
    trigger_t.setDaemon(True)
    trigger_t.start()
    threads['trigger'] = trigger_t

    monitor_t = threading.Thread(target=threadMonitorWorker, name='monitor')
    monitor_t.setDaemon(True)
    monitor_t.start()
    threads['monitor'] = monitor_t

    notify_t = threading.Thread(target=threadNotifyWorker, name='notifier')
    notify_t.setDaemon(True)
    notify_t.start()
    threads['notifier'] = notify_t

    env_t = threading.Thread(target=threadEnvWorker, name='env')
    env_t.setDaemon(True)
    env_t.start()
    threads['env'] = env_t

    for crawl_group_name, crawl_group_conf in env.crawl_conf.items():
        t = threading.Thread(target=threadCrawlWorker, name=crawl_group_name, kwargs=crawl_group_conf)
        t.setDaemon(True)
        t.start()

        threads['crawlers'][crawl_group_name] = t


    env.setThreads(threads)

    while True:
        time.sleep(59)


if __name__ == '__main__':
    cli()
