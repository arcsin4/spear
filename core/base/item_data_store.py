# -*- coding: utf-8 -*-
from core.env import env
from core.base.mysql_adapter import MysqlAdapter

class ItemDataStore(object):

    _mysql_yaml_path = None
    _mysql_adapter = None
    _db_name = 'sxy'

    def __init__(self):

        self._mysql_yaml_path = env.conf_dir + '/mysql.yaml'

        self._mysql_adapter = MysqlAdapter(mysql_yaml_path = self._mysql_yaml_path)

    #获取站点
    def getWebsites(self):

        db_name = self._db_name
        sql = """SELECT * FROM `website_list` WHERE 1=1 """
        res = self._mysql_adapter.fetch(sql_database_name=db_name, sql_statement=sql, sql_data=None)

        if len(res) > 0:
            return {r['website']: {'website_name':r['website_name'], 'url':r['url'], 'separately_keywords':int(r['separately_keywords']) } for r in res}

        return {}

    #获取关键字
    def getEventKeywords(self):

        db_name = self._db_name
        sql = """SELECT * FROM `event_keywords` WHERE 1=1 ORDER BY website ASC """
        res = self._mysql_adapter.fetch(sql_database_name=db_name, sql_statement=sql, sql_data=None)

        rtn = {}

        if len(res) > 0:
            for row in res:
                if row['website'] == '':
                    row['website'] = 'all'

                if row['website'] in rtn.keys():
                    rtn[row['website']].append(row['kw'])
                else:
                    rtn[row['website']] = [row['kw'], ]

        return rtn

    #获取爬虫结果记录
    def getCrawlResults(self, website, limit=100):

        db_name = self._db_name
        sql = """SELECT * FROM `crawl_result` WHERE website=%s ORDER BY news_time DESC, create_time DESC, pid DESC """
        data = [website, ]
        res = self._mysql_adapter.fetch(sql_database_name=db_name, sql_statement=sql, sql_data=data, fetch_num=limit)

        return res

    #保存记录
    def saveCrawlResults(self, data):

        db_name = self._db_name
        table_name = 'crawl_result'
        columns = ['website','pid', 'title','content','url','news_time','create_time']

        values = [ [x[y]  for y in columns] for x in data]

        return self._mysql_adapter.insertMany( sql_database_name = db_name, sql_table_name = table_name, columns = columns, values = values)

    #保存触发记录
    def saveTriggerMsg(self, data):

        db_name = self._db_name
        table_name = 'trigger_msg'
        columns = ['website','pid', 'trigger_words', 'title','content', 'origin', 'jump_url','news_time','create_time']

        return self._mysql_adapter.insertOne( sql_database_name = db_name, sql_table_name = table_name, columns = columns, values = data)


    #保存运行状态
    def saveRunningStatus(self, data):

        db_name = self._db_name

        columns = ['indicator','content']
        columns_updt = ['content']

        table_name = 'running_status'

        self._mysql_adapter.insertUpdate( sql_database_name = db_name, sql_table_name = table_name, columns = columns, values=data, columns_updt=columns_updt)

    #获取运行状态
    def getRunningStatus(self):

        db_name = self._db_name
        sql = """SELECT * FROM `running_status` WHERE 1=1 """
        res = self._mysql_adapter.fetch(sql_database_name=db_name, sql_statement=sql, sql_data=None)

        if len(res) > 0:
            return {r['indicator']: r['content'] for r in res}

        return {}

    #删除记录
    def cleanData(self, expire_time=0):

        db_name = self._db_name
        table_name_trigger = 'trigger_msg'
        table_name_crawl = 'crawl_result'

        where = {
            'news_time[<]': expire_time
        }

        self._mysql_adapter.deleteMany( sql_database_name = db_name, sql_table_name = table_name_trigger, where = where)
        self._mysql_adapter.deleteMany( sql_database_name = db_name, sql_table_name = table_name_crawl, where = where)
