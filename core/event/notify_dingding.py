# -*- coding: utf-8 -*-

from core.logger import system_log

import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode, quote_plus

from core.env import env

class NotifyDingding(object):

    _url = 'https://oapi.dingtalk.com/robot/send'

    _access_token = None

    _secret = None

    def __init__(self):

        super(NotifyDingding, self).__init__()

        self._access_token = env.notify_conf['dingding']['access_token']
        self._secret = env.notify_conf['dingding']['secret']

    def notify(self, head_kws=[], title='', content='', origin='', jump_url='', timestr='', send_count=1):

        timestamp, sign = self._generateSign()

        get_params = {
            'access_token': self._access_token,
            'timestamp': timestamp,
            'sign': sign,
        }

        url = self._url+'?'+urlencode(get_params)

        if origin is not None and origin != '':
            origin = '【'+origin+'】'
        else:
            origin = '点击查看'

        text = "### {}\n > **{}**".format(title,content)

        if timestr is not None and timestr != "":
            text = text + "\n\n{}   ".format(timestr)
        else:
            text = text + "\n\n   "

        if jump_url is not None and jump_url != "":
            text = text + "[{}]({})".format(origin, jump_url)

        head_title = title
        if len(head_kws) > 0:
            head_title = '【'+','.join(head_kws)+'】相关消息'
            text = "## "+head_title+"\n"+text

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title":head_title,
                "text": text,
            },
            "at": {
                "atMobiles": [],
                "isAtAll": False
            }
        }

        response = requests.post(url=url,data=json.dumps(data),headers={'Content-Type':'application/json'})
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            res = json.loads(response.text)
            if res['errcode'] == 0:
                system_log.debug('dingding notify success {}'.format(title))
                return True
            else:
                if res['errcode'] == 130101 and send_count <= 8:
                    time.sleep(10)
                    return self.notify(head_kws=head_kws, title=title, content=content, origin=origin, jump_url=jump_url, timestr=timestr, send_count=send_count+1)

                system_log.warning('dingding notify failed [{}] {}'.format(res['errcode'], res['errmsg']))

                return False

        system_log.debug('dingding notify failed {}'.format(response.status_code))
        return False

    def _generateSign(self):
        timestamp = str(round(time.time() * 1000))
        secret = self._secret
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = quote_plus(base64.b64encode(hmac_code))

        return timestamp, sign

notify_dingding = NotifyDingding()
