# -*- coding: utf-8 -*-

import requests
from urllib.parse import urlencode
from core.logger import system_log

class BaseCrawlRequest(object):
    _headers = None
    _session = None

    _website = ''

    def __init__(self):
        self._session = requests.Session()

    def post(self, url, post_data, headers=None):
        if headers is None:
            headers = self._headers

        try:
            response = self._session.post(url, data=post_data, headers=headers)
        except Exception as ex:
            system_log.error('{} post [{}] failed: {}'.format(self._website, url, ex))

            return None, None

        response.encoding = response.apparent_encoding

        #print(response)
        if response.status_code == 200:
            return response.status_code, response.text

        return response.status_code, None

    def get(self, url, get_params={}, headers=None):
        if headers is None:
            headers = self._headers

        params = urlencode(get_params)
        url = url + '?' + params

        try:
            response = self._session.get(url, headers=headers)
        except Exception as ex:
            system_log.error('{} get [{}] failed: {}'.format(self._website, url, ex))

            return None, None

        response.encoding = response.apparent_encoding

        if response.status_code == 200:
            return response.status_code, response.text

        return response.status_code, None
