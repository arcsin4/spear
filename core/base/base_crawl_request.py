# -*- coding: utf-8 -*-

import requests
from urllib.parse import urlencode
from core.logger import system_log

requests.DEFAULT_RETRIES = 5  # 增加重试连接次数

class BaseCrawlRequest(object):
    _headers = None
    _session = None
    _timeout = 10

    _website = ''
    # user_agent_list = [
    #     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    #     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    #     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    #     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    #     "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
    # ]

    def __init__(self):
        self._session = requests.Session()
        self._session.keep_alive = False

    def post(self, url, post_data, headers=None, proxies=None):
        if headers is None:
            headers = self._headers

        try:
            response = self._session.post(url, data=post_data, headers=headers, proxies=proxies, timeout=self._timeout)
        except Exception as ex:
            system_log.error('{} post [{}] failed: {}'.format(self._website, url, ex))

            return None, None

        response.encoding = response.apparent_encoding

        #print(response)
        if response.status_code == 200:
            return response.status_code, response.text

        return response.status_code, None

    def get(self, url, get_params={}, headers=None, proxies=None):
        if headers is None:
            headers = self._headers

        params = urlencode(get_params)
        url = url + '?' + params

        try:
            response = self._session.get(url, headers=headers, proxies=proxies, timeout=self._timeout)
        except Exception as ex:
            system_log.error('{} get [{}] failed: {}'.format(self._website, url, ex))

            return None, None

        response.encoding = response.apparent_encoding

        if response.status_code == 200:
            return response.status_code, response.text

        return response.status_code, None
