# -*- coding: utf-8 -*-

import requests
from urllib.parse import urlencode

class BaseCrawlRequest(object):
    _headers = None
    _session = None

    def __init__(self):
        self._session = requests.Session()

    def post(self, url, post_data):
        response = self._session.post(url, data=post_data, headers=self._headers)
        response.encoding = response.apparent_encoding

        #print(response)
        if response.status_code == 200:
            return response.status_code, response.text

        return response.status_code, None

    def get(self, url, get_params={}):
        params = urlencode(get_params)
        url = url + '?' + params

        response = self._session.get(url, headers=self._headers)
        response.encoding = response.apparent_encoding

        if response.status_code == 200:
            return response.status_code, response.text

        return response.status_code, None
