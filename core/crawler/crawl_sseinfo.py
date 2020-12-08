# -*- coding: utf-8 -*-
import time
import datetime
import re
import json

from core.env import env
from core.logger import system_log
from core.base.item_data_store import item_data_store
from core.crawler.base_crawl_request import BaseCrawlRequest
from bs4 import BeautifulSoup

class CrawlSseinfo(BaseCrawlRequest):

    _headers = {
            'Referer': 'http://sns.sseinfo.com/qa.do',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'sns.sseinfo.com',
    }

    _url = 'http://sns.sseinfo.com/ajax/feeds.do?type=11&pageSize={}&lastid=-1&show=1&page={}&_={}'
    _pagesize = 100

    _jumpurl = 'http://sns.sseinfo.com/qa.do'
    _website = 'sseinfo'

    _pids = None

    _time_res = {
        'seconds': re.compile('(\d+)秒前'),
        'minutes': re.compile('(\d+)分钟前'),
        'hours': re.compile('(\d+)小时前'),
        'yesterday': re.compile('昨天 ([\d\:]+)'),
        'md': re.compile('([\d\:\s月日]+)'),
    }

    _firstrun = True

    def __init__(self):

        super(CrawlSseinfo, self).__init__()

        res = item_data_store.getCrawlResults(website=self._website, limit=100)
        self._pids = set([str(r['pid']) for r in res])

    def _run(self, page):
        url = self._url.format(self._pagesize, page, str(int(time.time()*1000)))

        status_code, response = self.post(url=url, post_data={})

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            self.parseData(response)
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

    def run(self):

        if self._firstrun:
            system_log.info('sseinfo first run')
            for page in range(1, 5):
                self._run(page)
                time.sleep(1)

            self._firstrun = False
        else:
            self._run(1)

    def _parsetime(self, timestr):
        rr = re.fullmatch('(\d+)秒前', timestr, flags = 0)
        if rr is not None:
            d = int(rr.groups()[0])
            return datetime.datetime.now() + datetime.timedelta(seconds=-d)

        rr = re.fullmatch('(\d+)分钟前', timestr, flags = 0)
        if rr is not None:
            d = int(rr.groups()[0])
            return datetime.datetime.now() + datetime.timedelta(minutes=-d)

        rr = re.fullmatch('(\d+)小时前', timestr, flags = 0)
        if rr is not None:
            d = int(rr.groups()[0])
            return datetime.datetime.now() + datetime.timedelta(hours=-d)

        rr = re.fullmatch('昨天 ([\d\:]+)', timestr, flags = 0)
        if rr is not None:
            s = str(rr.groups()[0])

            x = datetime.datetime.now()+datetime.timedelta(days=-1)
            x2 = str(x.year)+'-'+str(x.month)+'-'+str(x.day)+' '+s

            return datetime.datetime.strptime(x2, '%Y-%m-%d %H:%M')

        rr = re.fullmatch('([\d\:\s月日]+)', timestr, flags = 0)
        if rr is not None:
            s = str(rr.groups()[0])
            s = str(datetime.date.today().year)+'年'+s
            rtn = datetime.datetime.strptime(s, '%Y年%m月%d日 %H:%M')
            if rtn - datetime.datetime.now() > datetime.timedelta(days=1):
                rtn = rtn.replace(year = datetime.date.today().year-1)
            return rtn

        rr = re.fullmatch('([\d\:\s年月日]+)', timestr, flags = 0)
        if rr is not None:
            s = str(rr.groups()[0])
            return datetime.datetime.strptime(s, '%Y年%m月%d日 %H:%M')

        return None

    def parseData(self, response):

        soup = BeautifulSoup(response , 'lxml')

        datas = []

        for e in soup.find_all(class_='m_feed_item'):

            pid = str(e.attrs['id'].split('-')[1])

            if pid in self._pids:
                break

            title = e.find(class_='m_feed_detail m_qa_detail').find(class_='m_feed_txt').get_text(separator=' ', strip=True).strip(' :')
            content = e.find(class_='m_feed_detail m_qa').find(class_='m_feed_txt').get_text(separator=' ', strip=True).strip()
            timestr = e.find(class_='m_feed_detail m_qa').find(class_='m_feed_from').find(name='span').get_text(separator=' ', strip=True).strip()

            jumpurl = self._jumpurl

            news_time = self._parsetime(timestr)
            if news_time is not None:
                news_time = int(time.mktime(news_time.timetuple()))
            else:
                news_time = int(time.time())


            d = [self._website, pid, title, content, jumpurl, news_time, int(time.time())]

            env.trigger_task_queue.put(json.dumps(d))

            datas.append(d)

        if len(datas) > 0:
            #['website','pid','title','content','url','news_time','create_time']
            item_data_store.saveCrawlResults(data = datas)

            for x in datas:
                self._pids.add(x[1])

        """
        <div class="m_feed_item" id="item-661910">
            <div class="m_feed_line"></div>
            <div class="m_feed_detail m_qa_detail">
                <div class="m_feed_face">
                    <a rel="face" uid="180453"
                            href="user.do?uid=180453" title="涨停养他"
                    alt="">
                    <img title="涨停养他" alt="" width="40" height="40" src="http://rs.sns.sseinfo.com/resources/images/avatar/202008/180453.png"></a>
                    <p>涨停养他</p>
                </div>
                <div class="m_feed_cnt ">
                            <div class="m_feed_info">
                                <div class="ask_ico index_ico" width="25" height="25"></div>
                            </div>
                            <div class="m_feed_txt" id="m_feed_txt-661910">
                                <a href='user.do?uid=105465' >:璞泰来(603659)</a>董秘您好，请问2020年三季度截止目前，贵司主营业务负极材料的年产能、存货量和市场占有率分别为多少？
                            </div>
                    <div class="m_feed_media">
                    </div>
                    <div class="m_feed_func">
                        <div class="m_feed_from">
                            <span>10月15日 16:41</span>
                            <em>来自</em>
                            <a href="javascript:;">网站</a>
                        </div>
                    </div>
                </div>
            </div>

            <div class="m_feed_detail m_qa">
                <div class="a_tit"><em class="S_line1_c">◆</em><span class="S_bg5_c">◆</span></div>

                <div class="m_feed_face">
                    <a class="ansface" rel="tag" uid="105465" href="user.do?uid=105465" title="璞泰来"><img title="璞泰来" alt="璞泰来" width="30" height="30" src="http://rs.sns.sseinfo.com/resources/images/avatar/company/603659.png"></a>
                    <p>璞泰来</p>
                </div>
                <div class="m_feed_cnt">
                    <div class="m_feed_info">
                        <div class="index_ico answer_ico"></div>
                    </div>
                    <div class="m_feed_txt" id="m_feed_txt-661910">
                        2020年全年公司负极材料的有效产能约7万吨，随着公司在石墨化和炭化产能的释放，存货周转也将逐渐加快；随着公司负极材料产能的进一步释放市场占有率尤其是中高端产品的市场占有率将获得进一步提升。
                    </div>
                    <div class="m_feed_media">
                    </div>
                </div>
                <div class="m_feed_func top10" style="margin-left: 70px;">
                    <div class="m_feed_handle">
                        <a href="javascript:love(661910);" id="love-661910"><em  ></em></a>
                        <i class="m_txt">|</i>

                        <a href="javascript:favorite(661910);" id="favorite-661910">收藏 </a>
                        <i class="m_txt">|</i>
                        <a href="javascript:comment(661910);">评论<span id="totalNum_661910"></span></a>
                    </div>
                    <div class="m_feed_share">
                        <!-- 分享插件 -->
                        <i class="index_ico weibo_ico" rel="sina-661910" onclick="toWeiBo('sina', '涨停养他', 661910);"></i>
                        <i class="index_ico qq_ico" rel="tx-661910" onclick="toWeiBo('tencent', '涨停养他', 661910);"></i>
                    </div>
                    <div class="m_feed_from" style="padding-left: 35px;">
                        <span>昨天 18:29</span>
                        <em>来自</em>
                                <a href="javascript:;">网站</a>
                    </div>
                    <div class="m_feed_type" id="love_list_661910" style="display: none;">
                    <div class="feed_quote">
                    <div class="q_tit l_p"><em class="S_line1_c S_line1_c1">◆</em>
                    <span class="S_bg4_c S_bg4_c1">◆</span></div>
                    <div class="q_con"><a href="javascript:pleaseLogin();">请登录后再点赞！</a>
                    </div><div class="q_btm"></div>
                    </div>
                    </div>
                    <div class="m_feed_type" id="favorite_list_661910" style="display: none;">
                        <div class="feed_quote">
                        <div class="q_tit l_f"><em class="S_line1_c S_line1_c1">◆</em>
                        <span class="S_bg4_c S_bg4_c1">◆</span></div>
                        <div class="q_con"><a href="javascript:pleaseLogin();">请登录后再收藏！</a>
                        </div><div class="q_btm"></div>
                        </div>
                    </div>
                    <div class="m_feed_comments" id="comment_list_661910"></div>
                </div>
            </div>
        </div>
        """