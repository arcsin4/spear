# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.item_data_store import ItemDataStore
from core.event.event_trigger import event_trigger
from core.crawler.base_crawl_request import BaseCrawlRequest

from bs4 import BeautifulSoup

from urllib.parse import urljoin

class CrawlCs(BaseCrawlRequest):

    _item_data_store = None

    _headers = {
            'Referer': 'http://www.cs.com.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'www.cs.com.cn',
    }

    _url = 'http://www.cs.com.cn/sylm/jsbd/'

    _website = 'cs'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(CrawlCs, self).__init__()

        self._item_data_store = ItemDataStore()

        res = self._item_data_store.getCrawlResults(website=self._website, limit=100)
        self._pids = set([str(r['pid']) for r in res])

    def _run(self):
        url = self._url

        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            self.parseData(response)
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

    def run(self):

        self._run()

    def parseData(self, response):

        soup = BeautifulSoup(response , 'lxml')

        datas = []

        for e in soup.find(class_='ch_type3_list').find_all(name='li'):

            pid = e.find(name='a').attrs['href']
            pid = pid.split('/')[-1]
            pid = pid.split('.')[0]

            if pid in self._pids:
                break

            #<li class="item"><a href="./202012/t20201201_6116434.html" target="_blank"><div><em>2020-12-01 18:59</em></div><h3>南风股份：中标5870万元项目</h3><span></span></a></li>

            news_time = int(time.mktime(time.strptime(e.find(name='em').get_text(separator=' ', strip=True).strip(), "%Y-%m-%d %H:%M")))
            title = e.find(name='h3').get_text(separator=' ', strip=True).strip()

            jumpurl = urljoin(self._url, e.find(name='a').attrs['href'])
            content = self._parseDataDetail(jumpurl)

            d = [self._website, pid, title, content, jumpurl, news_time, int(time.time())]

            env.trigger_task_queue.put(json.dumps(d))

            datas.append(d)

        if len(datas) > 0:
            #['website','pid','title','content','url','news_time','create_time']
            self._item_data_store.saveCrawlResults(data = datas)

            for x in datas:
                self._pids.add(x[1])

    def _parseDataDetail(self, url):

        content = None
        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            soup_detail = BeautifulSoup(response , 'lxml')

            content = '<br />'.join([x.get_text(separator=' ', strip=True).strip() for x in soup_detail.find(name='article').find(name='section').find_all(name='p')])
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

        return content






"""

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=gbk" />
<title>中证快讯 - 中证网</title>
<meta name="renderer" content="webkit"/>
<meta name="force-rendering" content="webkit"/>
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
<meta name="Keywords" content="证券,财经,经济,金融,时事,产业,民生,调查,聚焦,专题,时政,国内新闻,国际新闻,财经新闻,中证新闻,投教,投资者教育,中证,中国证券" />
<meta name="Description" content="中证新闻中心致力于为用户提供实时专业财经证券资讯,事件报导,国际国内新闻要点，覆盖宏观经济,金融市场,商业动态,上市公司,投资理财等全方位信息；" />
<meta name="baidu_union_verify" content="97b83a8cefe67878b9a68fc69b42d405">
<!--统计meta-->
<!--取消天润200910-->
<!--统计meta end-->
<link href="/css/2020/swiper.min.css" rel="stylesheet" type="text/css">
<link href="/css/2020/csj_index_2020.css" rel="stylesheet" type="text/css">
<link href="/css/2020/2020_channel.css" rel="stylesheet" type="text/css">

<script>/*@cc_on window.location.href="http://support.dmeng.net/upgrade-your-browser.html?referrer="+encodeURIComponent(window.location.href); @*/</script>
<script src="/js/2020/jquery-3.4.1.min.js"></script>
<script src="http://www.cs.com.cn/tj/csjtj_rltfiles/js/jquery.SuperSlide.2.1.3.js"></script>

</head>

<body>
<!--顶部导航1：会员红-->
<div class="mnone" style="width:100%; min-width:1200px; height:36px;"><iframe scrolling="no" src="http://www.cs.com.cn/cshtml/zzb_jntop2020/index.html" width="100%" min-width="1200" height="36" frameborder="0" ignoreapd="1"></iframe></div>
<!--顶部导航1：会员红 end-->
<!--顶部导航-->
<div class="box100p space_ptb2 topbg">
<div class="box1180">
<div class="logo_cs"><a href="http://www.cs.com.cn/"></a></div>
	<nav class="nv_all4 del_borrad nv_w">
		<ul>
			<li><a href="http://www.cs.com.cn/xwzx/" target="_blank">要闻</a></li>
			<li><a href="http://www.cs.com.cn/hyzblm/" target="_blank">直播汇</a></li>
			<li><a href="http://www.cs.com.cn/ssgs/" target="_blank">公司</a></li>
			<li><a href="http://www.cs.com.cn/xsb/" target="_blank">新三板</a></li>
			<li><a href="http://www.cs.com.cn/gppd/" target="_blank">市场</a></li>
			<li><a href="http://www.cs.com.cn/tzjj/" target="_blank">基金</a></li>
			<li><a href="http://www.cs.com.cn/lc/" target="_blank">理财</a></li>
			<li><a href="http://www.cs.com.cn/cj2020/" target="_blank">产经</a></li>
			<li><a href="http://www.cs.com.cn/fdc/" target="_blank">房产</a></li>
			<li><a href="http://xinpi.cs.com.cn/page/xp/index.html" target="_blank">信披</a></li>
			<li><a href="http://toujiao.cs.com.cn/" class="nv_link_special" target="_blank">投教基地</a></li>
			<li><a href="http://www.cs.com.cn/hw2020/" target="_blank">海外</a></li>
			<li><a href="http://video.cs.com.cn/" target="_blank">视频</a></li>
			<li><a href="http://www.cs.com.cn/xg/" target="_blank">新股</a></li>
			<li><a href="http://www.cs.com.cn/kcb2020/" target="_blank">科创板</a></li>
			<li><a href="http://www.cs.com.cn/qs/" target="_blank">券商</a></li>
			<li><a href="http://www.cs.com.cn/yh/" target="_blank">银行</a></li>
			<li><a href="http://www.cs.com.cn/bx/" target="_blank">保险</a></li>
			<li><a href="http://www.cs.com.cn/qc/" target="_blank">汽车</a></li>
			<li><a href="http://www.cs.com.cn/5g/" target="_blank">科技</a></li>
			<li><a href="http://stockdata.cs.com.cn/qcenter/new/hsmarket.html" target="_blank">行情</a></li>
			<li><a href="http://www.cs.com.cn/jnj/" class="nv_link_special" target="_blank">金牛专区</a></li>
		</ul>
	</nav>
  </div>
</div>
<!--顶部导航-->

<!--主体-->
<div class="box100p">
  <div class="box1180">
    <div class="box_ch space_t2">

  <!--左侧-->
     <div class="box_l1 space_r1">
<!--parent channel_name-->


<div class=" w100p ch_name  border_b">
	<h1 class="qkbys"><a href="../">首页</a></h1>
    <div><a href="./" target="_blank">中证快讯</a><a href="../syzt/" target="_blank">专题</a><a href="../cstop10/" target="_blank">公号精选</a></div>
</div>
<!--parent channel_name end-->
<!--channel_name-->
<h1 class="ctit space_b3  space_t2">中证快讯</h1>
<!--channel_name end-->
        <ul class="ch_type3_list some-list">

          <li class="item"><a href="./202012/t20201201_6116434.html" target="_blank"><div><em>2020-12-01 18:59</em></div><h3>南风股份：中标5870万元项目</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116433.html" target="_blank"><div><em>2020-12-01 18:57</em></div><h3>龙马环卫：公司及子公司累计收到政府补助3398.89万元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116432.html" target="_blank"><div><em>2020-12-01 18:56</em></div><h3>美尔雅：拟2.3亿元收购青海众友100%股权</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116430.html" target="_blank"><div><em>2020-12-01 18:55</em></div><h3>爱柯迪：股东拟减持不超2.18%公司股份</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116423.html" target="_blank"><div><em>2020-12-01 18:52</em></div><h3>天原集团：控股子公司收到产业入驻扶持资金1069万元</h3><span></span></a></li>

          <li class="item"><a href="../../xwzx/hg/202012/t20201201_6116416.html" target="_blank"><div><em>2020-12-01 18:46</em></div><h3>吉林省跨境电商健康有序发展 实现逆势增长</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116415.html" target="_blank"><div><em>2020-12-01 18:46</em></div><h3>兰石重装：公司及其子公司累计收到政府补助563.15万元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116414.html" target="_blank"><div><em>2020-12-01 18:45</em></div><h3>恒润股份：股东拟减持不超4.75%公司股份</h3><span></span></a></li>

          <li class="item"><a href="../../xwzx/hg/202012/t20201201_6116413.html" target="_blank"><div><em>2020-12-01 18:43</em></div><h3>贵州证监局：促进辖区私募行业合规健康发展</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116412.html" target="_blank"><div><em>2020-12-01 18:40</em></div><h3>信隆健康：股东拟减持约360万股</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116409.html" target="_blank"><div><em>2020-12-01 18:27</em></div><h3>西藏药业：股东拟减持不超2%公司股份</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116408.html" target="_blank"><div><em>2020-12-01 18:26</em></div><h3>鸿泉物联：拟出资5000万元参与中交兴路B轮融资</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116402.html" target="_blank"><div><em>2020-12-01 18:25</em></div><h3>厦门国贸：重组事项上会 12月2日起停牌</h3><span></span></a></li>

          <li class="item"><a href="../../5g/202012/t20201201_6116401.html" target="_blank"><div><em>2020-12-01 18:09</em></div><h3>多机构看好欢聚未来增长潜力</h3><span></span></a></li>

          <li class="item"><a href="../../tzjj/jjks/202012/t20201201_6116400.html" target="_blank"><div><em>2020-12-01 18:06</em></div><h3>北京和聚投资：顺周期板块行情正处于中场</h3><span></span></a></li>

          <li class="item"><a href="../../tzjj/jjdt/202012/t20201201_6116389.html" target="_blank"><div><em>2020-12-01 17:58</em></div><h3>刘全胜离任新华基金总经理</h3><span></span></a></li>

          <li class="item"><a href="../../ssgs/gsxw/202012/t20201201_6116388.html" target="_blank"><div><em>2020-12-01 17:53</em></div><h3>东软集团：子公司东软汉枫发布“物联网医废管理全系产品”</h3><span></span></a></li>

          <li class="item"><a href="../../ssgs/gsxw/202012/t20201201_6116386.html" target="_blank"><div><em>2020-12-01 17:47</em></div><h3>万业企业旗下凯世通签超1亿元集成电路设备订单</h3><span></span></a></li>

          <li class="item"><a href="../../xwzx/hg/202012/t20201201_6116385.html" target="_blank"><div><em>2020-12-01 17:35</em></div><h3>黑龙江证监局召开提高辖区上市公司质量专题座谈会</h3><span></span></a></li>

          <li class="item"><a href="../../ssgs/gsxw/202012/t20201201_6116376.html" target="_blank"><div><em>2020-12-01 17:13</em></div><h3>陌陌2020年第三季度净利润6.54亿元 持续23个季度盈利</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116375.html" target="_blank"><div><em>2020-12-01 17:08</em></div><h3>金银河：公司及全资子公司累计收到政府补助1176.96万元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116374.html" target="_blank"><div><em>2020-12-01 17:00</em></div><h3>华熙生物：股东拟减持不超1.8%公司股份</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116372.html" target="_blank"><div><em>2020-12-01 16:59</em></div><h3>瑞玛工业：累计收到政府补助771.33万元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116371.html" target="_blank"><div><em>2020-12-01 16:59</em></div><h3>中文传媒：签署23.3亿元采购合同</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116370.html" target="_blank"><div><em>2020-12-01 16:51</em></div><h3>广电网络：累计收到政府补助1388.1万元</h3><span></span></a></li>

          <li class="item"><a href="../../ssgs/gsxw/202012/t20201201_6116369.html" target="_blank"><div><em>2020-12-01 16:53</em></div><h3>光启技术12亿元订单首个批产合同正式落地</h3><span></span></a></li>

          <li class="item"><a href="../../tzjj/smjj/202012/t20201201_6116367.html" target="_blank"><div><em>2020-12-01 16:50</em></div><h3>诺亚控股发布三季报 前三季度非GAAP净利润达8.6亿元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116366.html" target="_blank"><div><em>2020-12-01 16:47</em></div><h3>12月1日在岸人民币涨120点</h3><span></span></a></li>

          <li class="item"><a href="../../xwzx/hg/202012/t20201201_6116365.html" target="_blank"><div><em>2020-12-01 16:46</em></div><h3>创业板指等深市三大核心指数调整样本股</h3><span></span></a></li>

          <li class="item"><a href="../../ssgs/gsxw/202012/t20201201_6116364.html" target="_blank"><div><em>2020-12-01 16:42</em></div><h3>中集模块化设计院助力 深圳福田区3个月建5所学校</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116363.html" target="_blank"><div><em>2020-12-01 16:37</em></div><h3>翔港科技：股东拟减持不超2%公司股份</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116362.html" target="_blank"><div><em>2020-12-01 16:37</em></div><h3>宝钢包装：12月2日开市起停牌</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116361.html" target="_blank"><div><em>2020-12-01 16:32</em></div><h3>保变电气：拟1200万元增资子公司</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116360.html" target="_blank"><div><em>2020-12-01 16:31</em></div><h3>三维股份：合营企业中标3.82亿元项目</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116359.html" target="_blank"><div><em>2020-12-01 16:30</em></div><h3>亿晶光电：全资子公司收到政府财政奖励4500万元</h3><span></span></a></li>

          <li class="item"><a href="../../tzjj/jjdt/202012/t20201201_6116358.html" target="_blank"><div><em>2020-12-01 16:30</em></div><h3>招商基金马龙：信用分化将成为债市发展必然趋势</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116357.html" target="_blank"><div><em>2020-12-01 16:29</em></div><h3>移远通信：公司及全资子公司累计收到政府补助1669.66万元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116352.html" target="_blank"><div><em>2020-12-01 16:25</em></div><h3>南卫股份：控股股东拟减持不超1%公司股份</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116348.html" target="_blank"><div><em>2020-12-01 16:24</em></div><h3>国检集团：拟对外投资6875万元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116345.html" target="_blank"><div><em>2020-12-01 16:22</em></div><h3>江苏阳光：控股股东增持1905.13万股公司股份</h3><span></span></a></li>

          <li class="item"><a href="../../xwzx/hg/202012/t20201201_6116333.html" target="_blank"><div><em>2020-12-01 16:08</em></div><h3>金标委：完善标准体系 服务数字金融</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116326.html" target="_blank"><div><em>2020-12-01 16:02</em></div><h3>央行：11月国开行、口行、农发行净归还抵押补充贷款1588亿元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116324.html" target="_blank"><div><em>2020-12-01 16:01</em></div><h3>央行：11月对金融机构开展中期借贷便利操作共10000亿元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116322.html" target="_blank"><div><em>2020-12-01 15:53</em></div><h3>央行：11月对金融机构开展常备借贷便利操作共81.5亿元</h3><span></span></a></li>

          <li class="item"><a href="./202012/t20201201_6116321.html" target="_blank"><div><em>2020-12-01 15:52</em></div><h3>财政部：支持培育完整内需体系 支持产业链供应链优化升级</h3><span></span></a></li>

        </ul>

    </div>

<!--右侧-->
<div class="box_r1">
<!--视频-->
<!--视频-->
				<div class="ch_video tab3 space_b3">
					<div class="ch_video_tab hd">
						<ul>
							<li class="on"><h2 class="ch_video_tt"><a href="http://video.cs.com.cn/" target="_blank">中证视频</a></h2></li>
							<li><h2 class="ch_video_tt"><a href="http://video.cs.com.cn/list.html?flag=0&sort=1&title=%E4%BC%A0%E9%97%BB%E6%B1%82%E8%AF%81&id=150&show=1" target="_blank">传闻求证</a></h2></li>
						</ul>
					</div>
					<div class="ch_video_cont bd">
						<ul>

							<li><a href="http://video.cs.com.cn/detail4.html?id=3596&flag=0&type=1" target="_blank"><span class="icon_vod1"></span><img src="../zzsp/202011/W020201128360275507846.png" alt="视频截图2.png"/><h3>百万新三板投资者翘首以盼的奔A重磅文件来了</h3></a></li>

							<li><a href="http://video.cs.com.cn/detail1.html?id=3558&flag=0&type=1" target="_blank"><span class="icon_vod1"></span><img src="../zzsp/202011/W020201105789015364388.png" alt="1604584370.png"/><h3>进博会车展看花眼，新能源车你PICK哪一款？</h3></a></li>

						</ul>
						<ul>

							<li><a href="http://video.cs.com.cn/150/3593.shtml?id=3593" target="_blank"><span class="icon_vod1"></span><img src="../cwqz/202011/W020201124712820657257.jpg" alt="360截图20201124194142265.jpg"/><h3>传水滴公司计划上市 腾讯追加1.5亿美元投资 公司回应</h3></a></li>

							<li><a href="http://video.cs.com.cn/150/3591.shtml?id=3591" target="_blank"><span class="icon_vod1"></span><img src="../cwqz/202011/W020201123550170051085.png" alt="1606090962(1).png"/><h3>菜鸟原副总裁史苗涉嫌受贿数百万 菜鸟回应</h3></a></li>

						</ul>
					</div>
				</div>
				<script>jQuery(".tab3").slide();</script>
				<!--视频 end-->
<!--视频 end-->
<!--直播汇-->


<div class="indepth_1">
				<h2 class="ch_typer2_tt"><a href="http://www.cs.com.cn/hyzblm/" target="_blank">直播汇<span>Live</span></a></h2>
				<ul>

					<li><a href="http://www.cs.com.cn/jnj/yhyjn/yhlc2020/" target="_blank"><img src="../../hyzblm/pic/202012/W020201201401880670850.jpg" alt="微信图片_20201201110524.jpg"/><h3>2020中国银行业理财发展论坛暨第一届中国银行业理财金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/zrz/600461/index.html" target="_blank"><img src="../../hyzblm/roadshow/202011/W020201118355144594606.jpg" alt="预告1.jpg"/><h3>洪城水业公开发行可转换公司债券网上路演</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/300910/index.html" target="_blank"><img src="../../hyzblm/roadshow/202011/W020201116484036822852.jpg" alt="预告1.jpg"/><h3>瑞丰新材首次公开发行股票并在创业板上市网上路演</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/htxc/index.html" target="_blank"><img src="../../hyzblm/roadshow/202011/W020201102537244409548.jpg" alt="500340.jpg"/><h3>会通新材首次公开发行A股并在科创板上市网上投资者交流会</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/688057/index.html" target="_blank"><img src="../../hyzblm/roadshow/202010/W020201029378394563152.jpg" alt="500340.jpg"/><h3>金达莱首次公开发行股票并在科创板上市网上投资者交流会</h3></a></li>

					<li><a href="http://www.cs.com.cn/hyzb/reits2020/" target="_blank"><img src="../../hyzblm/cjhy/202009/W020200927461934227400.jpg" alt="0.jpg"/><h3>中国REITs 论坛2020年会</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/003012/index.html" target="_blank"><img src="../../hyzblm/roadshow/202009/W020200925566361337409.jpg" alt="410280.jpg"/><h3>东鹏控股首次公开发行股票并在中小板上市网上路演</h3></a></li>

				</ul>
			</div>
<div class="blank30"></div>
<!--金牛-->


<div class="indepth_1 space_b3">
				<h2 class="ch_typer2_tt"><a href="../../jnj/" target="_blank">金牛奖<span>Golden Bull Awards</span></a></h2>
				<ul>

					<li><a href="http://www.cs.com.cn/jnj/yhyjn/yhlc2020/index.html" target="_blank"><img src="../../jnj/zxzs/202012/W020201201355509362253.jpg" alt="500340.jpg"/><h3>2020中国银行业理财发展论坛暨第一届中国银行业理财金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnfx/zqy2020/" target="_blank"><img src="../../jnj/zxzs/202012/W020201201412294948020.jpg" alt="ad_pic.jpg"/><h3>2020中国证券业高质量发展论坛</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jngs/ssgsjn2020/" target="_blank"><img src="../../jnj/zxzs/202011/W020201118526604053566.jpg" alt="500340.jpg"/><h3>2020上市公司高质量发展论坛暨第22届上市公司金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnjj/jnjj2020/" target="_blank"><img src="../../jnj/zxzs/202008/W020200822531694347540.jpg" alt="273183.jpg"/><h3>第十七届中国基金业金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnsm/jnsmhw2020/" target="_blank"><img src="../../jnj/zxzs/202008/W020200822295722734307.jpg" alt="ad_zbh.jpg"/><h3>第十一届中国私募金牛奖和第四届中国海外基金金牛奖</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnjj/jnfxh2020/" target="_blank"><img src="../../jnj/zxzs/202008/W020200821511759020685.jpg" alt="最新 和金牛奖.jpg"/><h3>“新机 新局 新使命” 2020金牛资产管理论坛</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnfx/zqy2019/" target="_blank"><img src="../../jnj/zxzs/201911/W020191121720897689120.jpg" alt="300165.jpg"/><h3>2019证券业高质量发展论坛</h3></a></li>

				</ul>
			</div>
<!--金牛 end-->
<!--信息可视化-->
<div class=" ad_right2 space_b3"><a href="http://gbclub.cs.com.cn/freeview.php?mod=kshcblist" target="_blank"><img src="../../cszz/syzz/adr300/adr3/201807/W020180710341275259065.jpg" alt="信息可视化30060.jpg"/></a></div>
<!--信息可视化 end-->
<!--投教-->
<div class="space_b3">
				<h2 class="ch_typer2_tt"><a href="http://toujiao.cs.com.cn/" target="_blank">投教基地<span></span></a></h2>
				<ul class="ch_typer_list">

					<li><a href="../../tj/02/01/202011/t20201127_6115482.html" target="_blank" title="重庆证监局联合公安经侦部门破获“撮某网”场外配资案">重庆证监局联合公安经侦部门破获“撮某网”场外配资案</a></li>

					<li><a href="../../tj/02/01/202011/t20201127_6115369.html" target="_blank" title="投资能力怎么样？ 8家险企自评估“成绩单”首次亮相">投资能力怎么样？ 8家险企自评估“成绩单”首次亮相</a></li>

					<li><a href="../../tj/02/01/202011/t20201126_6114894.html" target="_blank" title="使用数字人民币安全吗">使用数字人民币安全吗</a></li>

					<li><a href="../../tj/02/01/202011/t20201126_6114887.html" target="_blank" title="“户贷企用”频频爆雷，贫困户“救命钱”成了“唐僧肉”？">“户贷企用”频频爆雷，贫困户“救命钱”成了“唐僧肉”？</a></li>

				</ul>
			</div>
<!--投教 end-->
</div>
<!--右侧 end-->
    </div>
  </div>
</div>
<!--主体 end-->

<!--底部-->
<footer class="ft_site">
	<div class="box1180 ft_item">
    	<ul><li>关注</li><li><a href="http://www.cs.com.cn/aboutsite2020/gybs/" target="_blank">关于报社</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/gybz/" target="_blank">关于本站</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/bqsm/" target="_blank">版权声明</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/mztk/" target="_blank">免责条款</a></li></ul>
        <ul><li>合作</li><li><a href="http://www.cs.com.cn/aboutsite2020/ggfb/" target="_blank">广告发布</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/ggkl/" target="_blank">广告刊例</a></li></ul>
        <ul><li>服务</li><li><a href="http://epaper.cs.com.cn/dnis/acl.jsp" target="_blank">电子报</a></li><li><a href="http://xinpi.cs.com.cn/page/xp/index.html" target="_blank">信披平台</a></li><li><a href="http://www.cs.com.cn/zhzq/" target="_blank">服务平台</a></li><li><a href="http://gbclub.cs.com.cn/" target="_blank">中证金牛会</a></li></ul>
        <ul><li>旗下品牌</li><li><a href="http://cs.com.cn/jnj/" target="_blank">金牛奖</a></li><li><a href="http://toujiao.cs.com.cn/" target="_blank">投教基地</a></li></ul>
        <div class="bot_icon_spc"><img src="/images/2020/logo_wechat1.png" alt="wechat" /><div><img src="/images/2020/cs_qrc1.png" alt="wechat" /></div><span>中国证券报微信</span></div>
        <div class="bot_icon_spc"><img src="/images/2020/logo_weibo1.png" alt="weibo" /><div><img src="/images/2020/cs_qrc2.png" alt="weibo" /></div><span>中国证券报微博</span></div>
        <div class="bot_icon_spc"><img src="/images/2020/logo_app1.png" alt="app" /><div><img src="/images/2020/cs_qrc3.png" alt="app" /></div><span>中国证券报APP</span></div>
        <div class="bot_icon_spc"><img src="/images/2020/logo_tiktok1.png" alt="tiktok" /><div><img src="/images/2020/cs_qrc4.png" alt="tiktok" /></div><span>中国证券报抖音</span></div>
    </div>
    <div class="box1180 ft_gr">
    	<ul><li><a href="http://www.csrc.gov.cn/pub/newsite/" target="_blank">中国证券监督管理委员会</a></li><li><a href="http://www.sse.com.cn/" target="_blank">上海证券交易所</a></li><li><a href="http://www.szse.cn/" target="_blank">深圳证券交易所</a></li><li><a href="http://www.xinhuanet.com/" target="_blank">新华网</a></li><li><a href="http://ceis.xinhua08.com/a/20190326/1806626.shtml" target="_blank">新华财经APP</a></li><li><a href="http://www.cs.com.cn/link/links.htm" target="_blank">友情链接</a></li></ul>
    </div>
    <div class="box1180 ft_cr">
    	<span>中国证券报社版权所有，未经书面授权不得复制或建立镜像　经营许可证编号：京B2-20180749　京公网安备110102000060-1<br />Copyright　2001-2020　China Securities Journal.　All Rights Reserved</span>
    </div>
</footer>
<!--底部 end-->

<script src="/tj/mobile/jquery.simpleLoadMore.js" charset="utf-8"></script>
	<script>
	    $('.some-list').simpleLoadMore({
	      item: 'li.item',
	      count: 15
	    });
	</script>
<!--天润统计js-->
<!--取消天润200910-->
<!--天润统计js-->
</body>
</html>
"""

"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=gbk" />
<title>南风股份：中标5870万元项目_中证网</title>
<meta name="renderer" content="webkit"/>
<meta name="force-rendering" content="webkit"/>
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
<meta name="Keywords" content="南风股份" />
<meta name="Description" content="南风股份：中标5870万元项目" />
<meta name="baidu_union_verify" content="97b83a8cefe67878b9a68fc69b42d405">
<link rel="apple-touch-icon-precomposed" href="http://www.cs.com.cn/images/logo_wx.jpg" />
<link rel="shortcut icon" type="image/x-icon" href="/images/logo-cs.png" />
<link href="/css/2020/csj_index_2020.css" rel="stylesheet" type="text/css">
<link href="/css/2020/2020_channel.css" rel="stylesheet" type="text/css">
<script src="/js/2020/jquery-3.4.1.min.js"></script>
<script src="http://www.cs.com.cn/tj/csjtj_rltfiles/js/jquery.SuperSlide.2.1.3.js"></script>
<script type="text/javascript" src="http://res.wx.qq.com/open/js/jweixin-1.6.0.js"></script>
<script>
if(screen.width<480) //获取屏幕的的宽度
{ document.write('<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">');
}
else{}
</script>
<link rel="stylesheet" type="text/css" href="/css/2020/responsive-pc.css">
</head>

<body>

<!--顶部导航1：会员红-->
<div class="mnone" style="width:100%; min-width:1200px; height:36px;"><iframe scrolling="no" src="http://www.cs.com.cn/cshtml/zzb_jntop2020/index.html" width="100%" min-width="1200" height="36" frameborder="0" ignoreapd="1"></iframe></div>
<!--顶部导航1：会员红 end-->
<!--顶部导航-->
<div class="box100p space_ptb2 topbg">
<div class="box1180">
<div class="logo_cs"><a href="http://www.cs.com.cn/"></a></div>
	<nav class="nv_all4 del_borrad nv_w">
		<ul>
			<li><a href="http://www.cs.com.cn/xwzx/" target="_blank">要闻</a></li>
			<li><a href="http://www.cs.com.cn/hyzblm/" target="_blank">直播汇</a></li>
			<li><a href="http://www.cs.com.cn/ssgs/" target="_blank">公司</a></li>
			<li><a href="http://www.cs.com.cn/xsb/" target="_blank">新三板</a></li>
			<li><a href="http://www.cs.com.cn/gppd/" target="_blank">市场</a></li>
			<li><a href="http://www.cs.com.cn/tzjj/" target="_blank">基金</a></li>
			<li><a href="http://www.cs.com.cn/lc/" target="_blank">理财</a></li>
			<li><a href="http://www.cs.com.cn/cj2020/" target="_blank">产经</a></li>
			<li><a href="http://www.cs.com.cn/fdc/" target="_blank">房产</a></li>
			<li><a href="http://xinpi.cs.com.cn/page/xp/index.html" target="_blank">信披</a></li>
			<li><a href="http://toujiao.cs.com.cn/" class="nv_link_special" target="_blank">投教基地</a></li>
			<li><a href="http://www.cs.com.cn/hw2020/" target="_blank">海外</a></li>
			<li><a href="http://video.cs.com.cn/" target="_blank">视频</a></li>
			<li><a href="http://www.cs.com.cn/xg/" target="_blank">新股</a></li>
			<li><a href="http://www.cs.com.cn/kcb2020/" target="_blank">科创板</a></li>
			<li><a href="http://www.cs.com.cn/qs/" target="_blank">券商</a></li>
			<li><a href="http://www.cs.com.cn/yh/" target="_blank">银行</a></li>
			<li><a href="http://www.cs.com.cn/bx/" target="_blank">保险</a></li>
			<li><a href="http://www.cs.com.cn/qc/" target="_blank">汽车</a></li>
			<li><a href="http://www.cs.com.cn/5g/" target="_blank">科技</a></li>
			<li><a href="http://stockdata.cs.com.cn/qcenter/new/hsmarket.html" target="_blank">行情</a></li>
			<li><a href="http://www.cs.com.cn/jnj/" class="nv_link_special" target="_blank">金牛专区</a></li>
		</ul>
	</nav>
  </div>
</div>
<!--顶部导航-->
<!--手机端顶部导航-->
<div class="top-swiper fix">
 <a href="http://www.cs.com.cn/" class="nav_yw">返回首页</a>
</div>
<div class="hbox"></div>
<!--手机端顶部导航 end-->
<!-- 顶部广告 -->
<div class="box1180 ad1180">
<a href="http://www.cs.com.cn/common_files/xmt0517/" target="_blank"><img width="1180" height="80" style="border-left-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-top-width: 0px" alt="" oldsrc="W020180705414514225989.jpg" src="../../../cszz/xlad/ggxltop/201807/W020180705414514225989.jpg" /></a>
</div>
<!--line_content-->
<div class="box100p">
  <div class="box1180">
    <div class="box_ch space_t2 space_b3">
		<div class="box_l1 space_r1">
        <!--article-->
        <article class="cont_article">
        	<header>
            	<!--artc_route-->
				<div class="artc_route">
                	<div><a href="http://www.cs.com.cn/" target="_blank">首页</a>><a href="../" target="_blank" title="中证快讯" class="CurrChnlCls">中证快讯</a></div>
                </div>
				<!--artc_route end-->
        		<h1>南风股份：中标5870万元项目</h1>
                <h4></h4>
        		<div class="artc_info">
                	<div><em>王博</em><em>中国证券报·中证网</em><time>2020-12-01 18:59</time></div>
					<div class="bdsharebuttonbox share"><a href="#" class="bds_weixin" data-cmd="weixin" title="分享到微信"></a><a href="#" class="bds_tsina" data-cmd="tsina" title="分享到新浪微博"></a><a href="#" class="bds_more" data-cmd="more"></a></div>
                </div>
            </header>
            <section><style type="text/css">.TRS_Editor P{margin-top:0;}.TRS_Editor DIV{margin-top:0;}.TRS_Editor TD{margin-top:0;}.TRS_Editor TH{margin-top:0;}.TRS_Editor SPAN{margin-top:0;}.TRS_Editor FONT{margin-top:0;}.TRS_Editor UL{margin-top:0;}.TRS_Editor LI{margin-top:0;}.TRS_Editor A{margin-top:0;}</style><style type="text/css">

.TRS_Editor P{margin-top:0;}.TRS_Editor DIV{margin-top:0;}.TRS_Editor TD{margin-top:0;}.TRS_Editor TH{margin-top:0;}.TRS_Editor SPAN{margin-top:0;}.TRS_Editor FONT{margin-top:0;}.TRS_Editor UL{margin-top:0;}.TRS_Editor LI{margin-top:0;}.TRS_Editor A{margin-top:0;}</style>
<p>　　中证网讯（记者 王博）南风股份（300004）12月1日晚间公告，公司于近日收到上海中核浦原有限公司发出的中标通知书，公司被确认为“田湾核电站7、8号机组核岛余压阀、控制阀、止回阀、电加热阀设备采购”的中标方，中标金额5870万元。</p></section>

            <div class="page"><SCRIPT LANGUAGE="JavaScript">
var currentPage = 0;//所在页从0开始
var prevPage = currentPage-1//上一页
var nextPage = currentPage+1//下一页
var countPage = 1//共多少页

//设置上一页代码
if(countPage>1&&currentPage!=0&&currentPage!=1)
	document.write("<a href=\"t20201201_6116434"+"_" + prevPage + "."+"html\" target='_self'>上一页</a>");//加首页<a href=\"t20201201_6116434.html\" target='_self'>首页</a>
else if(countPage>1&&currentPage!=0&&currentPage==1)
	document.write("<a href=\"t20201201_6116434.html\" target='_self'>上一页</a>");
else
	document.write("");
//循环

var num = 20;
for(var i=0+(currentPage-1-(currentPage-1)%num) ; i<=(num+(currentPage-1-(currentPage-1)%num))&&(i<countPage) ; i++){
	if(currentPage==i&&countPage==1)
             document.write("");

	else if(currentPage==i)
		document.write("<span class=z_page_now>"+(i+1)+"</span>");
	else{
              if(i==0)
                   document.write("<a href=\"t20201201_6116434" + "."+"html\" target='_self'>"+(i+1)+"</a>");
                    else
		       document.write("<a href=\"t20201201_6116434"+"_" + i + "."+"html\" target='_self'>"+(i+1)+"</a>");
             }
}

//设置下一页代码
if(countPage>1&&currentPage!=(countPage-1))
	document.write("<a href=\"t20201201_6116434"+"_" + nextPage + "."+"html\" target='_self'>下一页</a>");//加尾页<a href=\"t20201201_6116434_" + (countPage-1) + ".html\" target='_self'>尾页</a>
else
	document.write("");

</SCRIPT></div>
            <footer>中证网声明：凡本网注明“来源：中国证券报·中证网”的所有作品，版权均属于中国证券报、中证网。中国证券报·中证网与作品作者联合声明，任何组织未经中国证券报、中证网以及作者书面授权不得转载、摘编或利用其它方式使用上述作品。凡本网注明来源非中国证券报·中证网的作品，均转载自其它媒体，转载目的在于更好服务读者、传递信息之需，并不代表本网赞同其观点，本网亦不对其真实性负责，持异议者应与原出处单位主张权利。</footer>
            <aside class="related_artlist">
            	<h2>相关阅读</h2>
            	<ul>

                	<li><span><time>2020-08-27 20:40</time></span><a href="../202008/t20200827_6089479.html" target="_blank" title="南风股份：上半年净利润8152.68万元 同比增长1035.3%">南风股份：上半年净利润8152.68万元 同比增长1035.3%</a></li>

                	<li><span><time>2019-12-17 17:04</time></span><a href="../201912/t20191217_6009215.html" target="_blank" title="南风股份：独董因减持前未披露减持计划收到警示函">南风股份：独董因减持前未披露减持计划收到警示函</a></li>

                	<li><span><time>2019-02-19 18:08</time></span><a href="../../../ssgs/gsxw/201902/t20190219_5924631.html" target="_blank" title="南风股份2018年净利润同比下降3707%">南风股份2018年净利润同比下降3707%</a></li>

                	<li><span><time>2019-01-31 08:59</time></span><a href="../201901/t20190131_5921129.html" target="_blank" title="南风股份收问询函 需说明商誉计提减值准备测算过程及合理性">南风股份收问询函 需说明商誉计提减值准备测算过程及合理性</a></li>

                	<li><span><time>2019-01-18 08:34</time></span><a href="../../../ssgs/gsxw/201901/t20190118_5916669.html" target="_blank" title="为前董事长债务担责 南风股份涉诉超亿元">为前董事长债务担责 南风股份涉诉超亿元</a></li>

                </ul>
            </aside>
        </article>
        <!--article end-->
    	</div>
  <!--右侧-->
<div class="box_r1">
<!--视频-->
<!--视频-->
				<div class="ch_video tab3 space_b3">
					<div class="ch_video_tab hd">
						<ul>
							<li class="on"><h2 class="ch_video_tt"><a href="http://video.cs.com.cn/" target="_blank">中证视频</a></h2></li>
							<li><h2 class="ch_video_tt"><a href="http://video.cs.com.cn/list.html?flag=0&sort=1&title=%E4%BC%A0%E9%97%BB%E6%B1%82%E8%AF%81&id=150&show=1" target="_blank">传闻求证</a></h2></li>
						</ul>
					</div>
					<div class="ch_video_cont bd">
						<ul>

							<li><a href="http://video.cs.com.cn/detail4.html?id=3596&flag=0&type=1" target="_blank"><span class="icon_vod1"></span><img src="../../zzsp/202011/W020201128360275507846.png" alt="视频截图2.png"/><h3>百万新三板投资者翘首以盼的奔A重磅文件来了</h3></a></li>

							<li><a href="http://video.cs.com.cn/detail1.html?id=3558&flag=0&type=1" target="_blank"><span class="icon_vod1"></span><img src="../../zzsp/202011/W020201105789015364388.png" alt="1604584370.png"/><h3>进博会车展看花眼，新能源车你PICK哪一款？</h3></a></li>

						</ul>
						<ul>

							<li><a href="http://video.cs.com.cn/150/3593.shtml?id=3593" target="_blank"><span class="icon_vod1"></span><img src="../../cwqz/202011/W020201124712820657257.jpg" alt="360截图20201124194142265.jpg"/><h3>传水滴公司计划上市 腾讯追加1.5亿美元投资 公司回应</h3></a></li>

							<li><a href="http://video.cs.com.cn/150/3591.shtml?id=3591" target="_blank"><span class="icon_vod1"></span><img src="../../cwqz/202011/W020201123550170051085.png" alt="1606090962(1).png"/><h3>菜鸟原副总裁史苗涉嫌受贿数百万 菜鸟回应</h3></a></li>

						</ul>
					</div>
				</div>
				<script>jQuery(".tab3").slide();</script>
				<!--视频 end-->
<!--视频 end-->
<!--直播汇-->

<div class="indepth_1">
				<h2 class="ch_typer2_tt"><a href="http://www.cs.com.cn/hyzblm/" target="_blank">直播汇<span>Live</span></a></h2>
				<ul>

					<li><a href="http://www.cs.com.cn/jnj/yhyjn/yhlc2020/" target="_blank"><img src="../../../hyzblm/pic/202012/W020201201401880670850.jpg" alt="微信图片_20201201110524.jpg"/><h3>2020中国银行业理财发展论坛暨第一届中国银行业理财金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/zrz/600461/index.html" target="_blank"><img src="../../../hyzblm/roadshow/202011/W020201118355144594606.jpg" alt="预告1.jpg"/><h3>洪城水业公开发行可转换公司债券网上路演</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/300910/index.html" target="_blank"><img src="../../../hyzblm/roadshow/202011/W020201116484036822852.jpg" alt="预告1.jpg"/><h3>瑞丰新材首次公开发行股票并在创业板上市网上路演</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/htxc/index.html" target="_blank"><img src="../../../hyzblm/roadshow/202011/W020201102537244409548.jpg" alt="500340.jpg"/><h3>会通新材首次公开发行A股并在科创板上市网上投资者交流会</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/688057/index.html" target="_blank"><img src="../../../hyzblm/roadshow/202010/W020201029378394563152.jpg" alt="500340.jpg"/><h3>金达莱首次公开发行股票并在科创板上市网上投资者交流会</h3></a></li>

					<li><a href="http://www.cs.com.cn/hyzb/reits2020/" target="_blank"><img src="../../../hyzblm/cjhy/202009/W020200927461934227400.jpg" alt="0.jpg"/><h3>中国REITs 论坛2020年会</h3></a></li>

					<li><a href="http://www.cs.com.cn/roadshow/ipo/003012/index.html" target="_blank"><img src="../../../hyzblm/roadshow/202009/W020200925566361337409.jpg" alt="410280.jpg"/><h3>东鹏控股首次公开发行股票并在中小板上市网上路演</h3></a></li>

				</ul>
			</div>
<div class="blank30"></div>
<!--金牛-->

<div class="indepth_1 space_b3">
				<h2 class="ch_typer2_tt"><a href="../../../jnj/" target="_blank">金牛奖<span>Golden Bull Awards</span></a></h2>
				<ul>

					<li><a href="http://www.cs.com.cn/jnj/yhyjn/yhlc2020/index.html" target="_blank"><img src="../../../jnj/zxzs/202012/W020201201355509362253.jpg" alt="500340.jpg"/><h3>2020中国银行业理财发展论坛暨第一届中国银行业理财金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnfx/zqy2020/" target="_blank"><img src="../../../jnj/zxzs/202012/W020201201412294948020.jpg" alt="ad_pic.jpg"/><h3>2020中国证券业高质量发展论坛</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jngs/ssgsjn2020/" target="_blank"><img src="../../../jnj/zxzs/202011/W020201118526604053566.jpg" alt="500340.jpg"/><h3>2020上市公司高质量发展论坛暨第22届上市公司金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnjj/jnjj2020/" target="_blank"><img src="../../../jnj/zxzs/202008/W020200822531694347540.jpg" alt="273183.jpg"/><h3>第十七届中国基金业金牛奖颁奖典礼</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnsm/jnsmhw2020/" target="_blank"><img src="../../../jnj/zxzs/202008/W020200822295722734307.jpg" alt="ad_zbh.jpg"/><h3>第十一届中国私募金牛奖和第四届中国海外基金金牛奖</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnjj/jnfxh2020/" target="_blank"><img src="../../../jnj/zxzs/202008/W020200821511759020685.jpg" alt="最新 和金牛奖.jpg"/><h3>“新机 新局 新使命” 2020金牛资产管理论坛</h3></a></li>

					<li><a href="http://www.cs.com.cn/jnj/jnfx/zqy2019/" target="_blank"><img src="../../../jnj/zxzs/201911/W020191121720897689120.jpg" alt="300165.jpg"/><h3>2019证券业高质量发展论坛</h3></a></li>

				</ul>
			</div>
<!--金牛 end-->
<!--广告-->
<div class=" ad_right2 space_b3"><a href="../../../cszz/xlad/xlrad/201409/t20140904_4503344.html" target="_blank"></a></div>
<!--广告 end-->
<!--投教-->
<div class="space_b3">
				<h2 class="ch_typer2_tt"><a href="http://toujiao.cs.com.cn/" target="_blank">投教基地<span></span></a></h2>
				<ul class="ch_typer_list">

					<li><a href="../../../tj/02/01/202011/t20201127_6115482.html" target="_blank" title="重庆证监局联合公安经侦部门破获“撮某网”场外配资案">重庆证监局联合公安经侦部门破获“撮某网”场外配资案</a></li>

					<li><a href="../../../tj/02/01/202011/t20201127_6115369.html" target="_blank" title="投资能力怎么样？ 8家险企自评估“成绩单”首次亮相">投资能力怎么样？ 8家险企自评估“成绩单”首次亮相</a></li>

					<li><a href="../../../tj/02/01/202011/t20201126_6114894.html" target="_blank" title="使用数字人民币安全吗">使用数字人民币安全吗</a></li>

					<li><a href="../../../tj/02/01/202011/t20201126_6114887.html" target="_blank" title="“户贷企用”频频爆雷，贫困户“救命钱”成了“唐僧肉”？">“户贷企用”频频爆雷，贫困户“救命钱”成了“唐僧肉”？</a></li>

				</ul>
			</div>
<!--投教 end-->

</div>
<!--右侧 end-->
    </div>
  </div>
</div>
<!--line_content end-->

<!--底部-->
<footer class="ft_site">
	<div class="box1180 ft_item">
    	<ul><li>关注</li><li><a href="http://www.cs.com.cn/aboutsite2020/gybs/" target="_blank">关于报社</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/gybz/" target="_blank">关于本站</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/bqsm/" target="_blank">版权声明</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/mztk/" target="_blank">免责条款</a></li></ul>
        <ul><li>合作</li><li><a href="http://www.cs.com.cn/aboutsite2020/ggfb/" target="_blank">广告发布</a></li><li><a href="http://www.cs.com.cn/aboutsite2020/ggkl/" target="_blank">广告刊例</a></li></ul>
        <ul><li>服务</li><li><a href="http://epaper.cs.com.cn/dnis/acl.jsp" target="_blank">电子报</a></li><li><a href="http://xinpi.cs.com.cn/page/xp/index.html" target="_blank">信披平台</a></li><li><a href="http://www.cs.com.cn/zhzq/" target="_blank">服务平台</a></li><li><a href="http://gbclub.cs.com.cn/" target="_blank">中证金牛会</a></li></ul>
        <ul><li>旗下品牌</li><li><a href="http://cs.com.cn/jnj/" target="_blank">金牛奖</a></li><li><a href="http://toujiao.cs.com.cn/" target="_blank">投教基地</a></li></ul>
        <div class="bot_icon_spc"><img src="/images/2020/logo_wechat1.png" alt="wechat" /><div><img src="/images/2020/cs_qrc1.png" alt="wechat" /></div><span>中国证券报微信</span></div>
        <div class="bot_icon_spc"><img src="/images/2020/logo_weibo1.png" alt="weibo" /><div><img src="/images/2020/cs_qrc2.png" alt="weibo" /></div><span>中国证券报微博</span></div>
        <div class="bot_icon_spc"><img src="/images/2020/logo_app1.png" alt="app" /><div><img src="/images/2020/cs_qrc3.png" alt="app" /></div><span>中国证券报APP</span></div>
        <div class="bot_icon_spc"><img src="/images/2020/logo_tiktok1.png" alt="tiktok" /><div><img src="/images/2020/cs_qrc4.png" alt="tiktok" /></div><span>中国证券报抖音</span></div>
    </div>
    <div class="box1180 ft_gr">
    	<ul><li><a href="http://www.csrc.gov.cn/pub/newsite/" target="_blank">中国证券监督管理委员会</a></li><li><a href="http://www.sse.com.cn/" target="_blank">上海证券交易所</a></li><li><a href="http://www.szse.cn/" target="_blank">深圳证券交易所</a></li><li><a href="http://www.xinhuanet.com/" target="_blank">新华网</a></li><li><a href="http://ceis.xinhua08.com/a/20190326/1806626.shtml" target="_blank">新华财经APP</a></li><li><a href="http://www.cs.com.cn/link/links.htm" target="_blank">友情链接</a></li></ul>
    </div>
    <div class="box1180 ft_cr">
    	<span>中国证券报社版权所有，未经书面授权不得复制或建立镜像　经营许可证编号：京B2-20180749　京公网安备110102000060-1<br />Copyright　2001-2020　China Securities Journal.　All Rights Reserved</span>
    </div>
</footer>
<!--底部 end-->
<!--移动底部-->
<footer class="mfooter">
   <div class="mfooter-l">中国证券报社版权所有，未经书面授权不得复制或建立镜像。 <br />Copyright &copy; 2001-2020　China Securities Journal.All Rights Reserved.</div>
<div class="mfooter-r"><section><img src="/images/2020/cs_qrc1.png" alt="pic" /><span>中国证券报微信</span></section><section><img src="/images/2020/cs_qrc3.png" alt="pic" /><span>中国证券报APP</span></section><section><img src="/images/2020/cs_qrc4.png" alt="pic" /><span>中国证券报抖音</span></section></div>
   </footer>
<!--移动底部-->

<!--微信分享-->
  <script type="text/javascript">
   var link = location.href.split("#")[0];
   $.ajax({
    url: "http://gbclub.cs.com.cn/csfuncs/cs2020funcs/getWxInfo", //后台提供的接口
    type: "GET",
    data: {
     "url": link
    },
    async: true,
    dataType: "json",
    success: function(data) {
     console.log(data)
     wx.config({
      debug: false,
      appId: data.appId,
      timestamp: data.timestamp,
      nonceStr: data.nonceStr,
      signature: data.signature,
      jsApiList: [
       "updateAppMessageShareData",
       "updateTimelineShareData",
       "onMenuShareTimeline",
       "onMenuShareAppMessage"
      ]
     });
     wx.error(function(res) {
      console.log(res)

     });
    },
    error: function(error) {

    }
   });

   wx.ready(function() {
    //自定义“分享给朋友”及“分享到QQ”按钮的分享内容（1.4.0）
    wx.updateAppMessageShareData({
     title:"南风股份：中标5870万元项目",
     desc: "中国证券报（ID:wwwcscomcn）",
     link: link,
     imgUrl: "http://www.cs.com.cn/images/logo_wx.jpg", // 分享图标
     success: function () {
       // 设置成功
     }
    });

    //自定义“分享到朋友圈”及“分享到QQ空间”按钮的分享内容（1.4.0）
    wx.updateTimelineShareData({
     title:"南风股份：中标5870万元项目",
     desc: "中国证券报（ID:wwwcscomcn）",
     link: link,
     // 分享链接，该链接域名或路径必须与当前页面对应的公众号JS安全域名一致
     imgUrl: "http://www.cs.com.cn/images/logo_wx.jpg", // 分享图标
     success: function () {
       // 设置成功
     }
      });
      wx.onMenuShareAppMessage({
     title:"南风股份：中标5870万元项目",
     desc: "中国证券报（ID:wwwcscomcn）",
     link: link,
     imgUrl: "http://www.cs.com.cn/images/logo_wx.jpg",
     trigger: function(res) {},
     success: function(res) {},
     cancel: function(res) {},
     fail: function(res) {}
    });

    wx.onMenuShareTimeline({
     title:"南风股份：中标5870万元项目",
     desc: "中国证券报（ID:wwwcscomcn）",
     link: link,
     imgUrl: "http://www.cs.com.cn/images/logo_wx.jpg",
     trigger: function(res) {},
     success: function(res) {},
     cancel: function(res) {},
     fail: function(res) {}
    });
   });
  </script>
 <!--微信分享结束-->

<script>window._bd_share_config={"common":{"bdSnsKey":{},"bdText":"","bdMini":"2","bdMiniList":false,"bdPic":"","bdStyle":"0","bdSize":"16"},"share":{}};with(document)0[(getElementsByTagName('head')[0]||body).appendChild(createElement('script')).src='http://bdimg.share.baidu.com/static/api/js/share.js?v=89860593.js?cdnversion='+~(-new Date()/36e5)];</script>

</body>
</html>
"""