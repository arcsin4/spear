# -*- coding: utf-8 -*-
import yaml
import pymysql
import contextlib
import re

class MysqlAdapter(object):
    # 初始化
    def __init__(self, mysql_yaml_path):
        self._conn = {}
        self._mysql_yaml_path = mysql_yaml_path
        # 加载配置
        with open(self._mysql_yaml_path, 'r', encoding='utf-8') as f:
            self._sql_conf = yaml.load(f.read(), Loader=yaml.FullLoader)

    #定义上下文管理器，连接后自动关闭连接
    @contextlib.contextmanager
    def _cursor(self, sql_database_name):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        # 创建连接
        try:
            assert sql_database_name in self._conn
            self._conn[sql_database_name].ping(reconnect=True)
        except:
            self._conn[sql_database_name] = pymysql.connect(host=self._sql_conf['host'], port=self._sql_conf['port'], user=self._sql_conf['user'], passwd=self._sql_conf['password'], db=sql_database_name, charset='utf8')
        conn = self._conn[sql_database_name]
        # 创建游标
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            yield cursor
        finally:
            # 提交，不然无法保存新建或者修改的数据
            conn.commit()
            # 关闭游标
            cursor.close()
            # 关闭连接
            conn.close()

    def _execute(self, sql_database_name, sql_statement, sql_data, many=False):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_statement, str) and len(sql_statement) > 0
        assert isinstance(sql_data, list) and len(sql_data) > 0
        res = True
        row_count = 0
        # 执行sql
        with self._cursor(sql_database_name) as cursor:
            try:
                if many == True:
                    row_count = cursor.executemany(sql_statement, sql_data)
                else:
                    row_count = cursor.execute(sql_statement, sql_data)
            except Exception:
                res = False
        return (res, row_count)

    def _fetch(self, sql_database_name, sql_statement, sql_data=None, fetch_num=None):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_statement, str) and len(sql_statement) > 0
        assert sql_data is None or (isinstance(sql_data, list) and len(sql_data) > 0 )
        assert fetch_num is None or ( isinstance(fetch_num, int) and fetch_num > 0 )

        rtn = None

        # 执行sql
        with self._cursor(sql_database_name) as cursor:
            try:
                # 执行SQL，并返回受影响行数
                cursor.execute(sql_statement, sql_data)
                if fetch_num is None:
                    # 获取剩余结果所有数据
                    rtn = cursor.fetchall()
                elif fetch_num <= 1:
                    # 获取剩余结果的第一行数据
                    rtn = cursor.fetchone()
                else:
                    # 获取剩余结果所有数据
                    rtn = cursor.fetchall()
            except Exception:
                return None

        return rtn

    def _analyzingWhere(self, where_dict: dict) -> tuple():
        assert isinstance(where_dict, dict)
        data = []
        if where_dict:
            where_arr = []
            for key, val in where_dict.items():
                data.append(val)
                key_match = re.match(r"^([^\[]+)(\[*)([^\]]*)(\]*)$", key)
                if key_match is None:
                    raise ValueError("where key wrong : " + str(key))
                key = str(key_match.group(1))
                if len(key_match.group(3)):
                    action = key_match.group(3)
                else:
                    action = '='
                where_row = "`"+pymysql.escape_string(key)+"` "+action+" %s"
                where_arr.append(where_row)
            where_sql = " AND ".join([row for row in where_arr])
        else:
            where_sql = ""
        return (where_sql, data)

    def insertOne(self, sql_database_name, sql_table_name, columns, values):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_table_name, str) and len(sql_table_name) > 0
        assert isinstance(columns, list) and len(columns) > 0
        assert isinstance(values, list) and len(values) > 0
        assert len(columns) == len(values)

        sql_column = ",".join(["`"+pymysql.escape_string(str(k))+"`" for k in columns])
        sql_values = ",".join(["%s" for _ in values])

        data = values

        # 执行SQL，并返回受影响行数
        sql = "INSERT IGNORE INTO " + sql_table_name + " (" + sql_column + ") VALUES (" + sql_values + ") "

        return self._execute(sql_database_name, sql, data, many=False)


    def insertMany(self, sql_database_name, sql_table_name, columns, values):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_table_name, str) and len(sql_table_name) > 0
        assert isinstance(columns, list) and len(columns) > 0
        assert isinstance(values, list) and len(values) > 0


        sql_column = ",".join(["`"+pymysql.escape_string(str(k))+"`" for k in columns])

        sql_values = ",".join(["%s" for _ in columns])

        data = values

        # 执行SQL，并返回受影响行数
        sql = "INSERT IGNORE INTO " + sql_table_name + " (" + sql_column + ") VALUES (" + sql_values + ") "

        return self._execute(sql_database_name, sql, data, many=True)


    def insertUpdate(self, sql_database_name, sql_table_name, columns, values, columns_updt):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_table_name, str) and len(sql_table_name) > 0
        assert isinstance(columns, list) and len(columns) > 0
        assert isinstance(values, list) and len(values) > 0
        assert isinstance(columns_updt, list) and len(columns_updt) > 0

        sql_column = ",".join(["`"+pymysql.escape_string(str(k))+"`" for k in columns])

        sql_values = ",".join(["(" + ",".join(["%s" for k in c]) + ")" for c in values])

        sql_updt = ",".join(["`"+pymysql.escape_string(str(k))+"` = values(`"+pymysql.escape_string(str(k))+"`)" for k in columns_updt])

        data = []
        for c in values:
            data.extend(c)

        # 执行SQL，并返回受影响行数
        sql = "INSERT INTO " + sql_table_name + " (" + sql_column + ") VALUES " + sql_values + " ON DUPLICATE KEY UPDATE " + sql_updt + " "
        return self._execute(sql_database_name, sql, data, many=False)


    def updateSave(self, sql_database_name, sql_table_name, setdata, where=None):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_table_name, str) and len(sql_table_name) > 0
        assert isinstance(setdata, dict) and len(setdata) > 0
        assert where is None or (isinstance(where, dict) and len(where) > 0)

        data = []
        keyArr = []
        for key, val in setdata.items():
            keyArr.append(key)
            data.append(val)
        sql_set = ",".join(["`"+pymysql.escape_string(str(key))+"`=%s" for key in keyArr])

        sql_where = ""
        if where:
            where_str, where_data = self._analyzingWhere(where_dict=where)
            sql_where = " WHERE " + where_str
            data.append(where_data)

        # 执行SQL，并返回受影响行数
        sql = "UPDATE `" + sql_table_name + "` SET " + sql_set + sql_where
        return self._execute(sql_database_name, sql, data, many=False)


    def deleteMany(self, sql_database_name, sql_table_name, where):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_table_name, str) and len(sql_table_name) > 0
        assert isinstance(where, dict) and len(where) > 0

        where_sql, data = self._analyzingWhere(where_dict=where)
        # 执行SQL，并返回受影响行数
        sql = "DELETE FROM " + sql_table_name + " WHERE " + where_sql

        return self._execute(sql_database_name, sql, data, many=False)

    def fetch(self, sql_database_name, sql_statement, sql_data=None, fetch_num=None):
        assert isinstance(sql_database_name, str) and len(sql_database_name) > 0
        assert isinstance(sql_statement, str) and len(sql_statement) > 0
        assert sql_data is None or (isinstance(sql_data, list) and len(sql_data) > 0 )
        assert fetch_num is None or ( isinstance(fetch_num, int) and fetch_num > 0 )

        return self._fetch(sql_database_name, sql_statement, sql_data, fetch_num)
