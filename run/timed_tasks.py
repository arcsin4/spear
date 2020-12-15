# -*- coding: utf-8 -*-

import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__),os.path.pardir,os.path.pardir))
CONF_DIR = os.path.join(BASE_DIR, 'conf')
sys.path.append(BASE_DIR) #把上级目录加入到变量中

from core.env import env
env.setConfDir(conf_dir = CONF_DIR)
env.loadEnvCfg()

import traceback
import click
import time
import datetime

from core.logger import system_log

from core.base.item_data_store import ItemDataStore

item_data_store = ItemDataStore()


@click.group()
@click.help_option('-h', '--help')
def cli():
    '''执行定时任务程序'''
    pass

@cli.command()
@click.help_option('-h', '--help')
def cleanData(log_level='info'):
    '''清理历史数据'''

    try:
        data_keep_days = int(env.env_conf['data_keep_days']['value'])
        system_log.info('start clean data over {} days'.format(data_keep_days))


        expire_time = datetime.date.today() + datetime.timedelta(days=-data_keep_days)
        expire_time = int(time.mktime(expire_time.timetuple()))

        item_data_store.cleanData(expire_time=expire_time)

        system_log.info('clean data finished '.format(data_keep_days))

    except Exception as ex:
        system_log.error('clean data error: {} {}'.format(ex, str(traceback.format_exc())))
        raise


if __name__ == '__main__':
    cli()
