# -*- coding: utf-8 -*-
import time
import json

from core.env import env
from core.logger import system_log
from core.base.item_data_store import ItemDataStore
from core.crawler.base_crawl_request import BaseCrawlRequest
from bs4 import BeautifulSoup

class Crawl36kr(BaseCrawlRequest):

    _item_data_store = None

    _headers = {
            'Referer': 'https://36kr.com/newsflashes',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': '36kr.com',
    }

    _headers_next = {
            'Referer': 'https://36kr.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'content-type': 'application/json',
    }

    _url = 'https://36kr.com/newsflashes'
    _url_next = 'https://gateway.36kr.com/api/mis/nav/newsflash/flow'

    _jumpurl = 'https://36kr.com/newsflashes/{}'
    _website = '36kr'

    _pids = None

    _firstrun = True

    def __init__(self):

        super(Crawl36kr, self).__init__()

        self._item_data_store = ItemDataStore()

        self.refreshPids()

    def refreshPids(self):

        res = self._item_data_store.getCrawlResults(website=self._website, limit=100)
        self._pids = set([str(r['pid']) for r in res])

    def _chkPidExist(self, pid):
        return str(pid) in self._pids

    def _addPid(self, pid):
        self._pids.add(str(pid))

    def _runNext(self, page_callback):
        url = self._url

        post_data = {
            'param': {
                'pageEvent': 1,
                'pageSize': 1000,
                'pageCallback': page_callback,
                'platformId': 2,
                'siteId': 1,
            },
            'partner_id': "web",
            'timestamp': int(time.time()*1000),
        }

        status_code, response = self.post(url=self._url_next, post_data=json.dumps(post_data), headers=self._headers_next)

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            return self.parseData(response, next=True)
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

    def _run(self):
        url = self._url

        status_code, response = self.get(url=url, get_params={})

        if status_code == 200:
            system_log.debug('runCrawl success [{}] {}'.format(status_code, url))

            return self.parseData(response)
        else:
            system_log.error('runCrawl failed [{}] {}'.format(status_code, url))

    def run(self):

        page_callback = self._run()

        if self._firstrun:
            system_log.info('36kr first run')

            page_callback = self._runNext(page_callback)
            time.sleep(1)
            self._firstrun = False

    def parseData(self, response, next = False):

        if not next:
            soup = BeautifulSoup(response , 'lxml')

            res = soup.body.find(name='script').string.strip()
            res = res[res.find('{'):]
            res = json.loads(res)

            page_callback = res['newsflashCatalogData']['data']['newsflashList']['data']['pageCallback']
            has_nextpage = res['newsflashCatalogData']['data']['newsflashList']['data']['hasNextPage']

            item_list = res['newsflashCatalogData']['data']['newsflashList']['data']['itemList']

        else:
            res = json.loads(response)

            page_callback = res['data']['pageCallback']
            has_nextpage = res['data']['hasNextPage']

            item_list = res['data']['itemList']

        datas = []
        for item in item_list:
            pid = str(item['itemId'])

            if self._chkPidExist(pid):
                break

            title = item['templateMaterial']['widgetTitle']
            content = item['templateMaterial']['widgetContent']
            news_time = int(item['templateMaterial']['publishTime'])//1000

            jumpurl = self._jumpurl.format(pid)

            d = [self._website, pid, title, content, jumpurl, news_time, int(time.time())]

            env.trigger_task_queue.put(json.dumps(d))

            datas.append(d)

        if len(datas) > 0:
            #['website','pid','title','content','url','news_time','create_time']
            self._item_data_store.saveCrawlResults(data = datas)

            for x in datas:
                self._addPid(x[1])

        if int(has_nextpage) >= 1 and len(page_callback) > 0:
            return page_callback

        return ''

        """
        <body>
            <script>window.initialState = { "navigator": { "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36" }, "theme": "default", "newsflashCatalogData": { "code": 0, "data": { "newsflashList": { "code": 0, "data": { "itemList": [{ "itemId": 1007544256052737, "itemType": 20, "templateMaterial": { "itemId": 1007544256052737, "templateType": 0, "publishTime": 1607767621096, "widgetTitle": "布瑞克首届“农产品采购狂欢节”预计全天销售额突破1亿元", "widgetContent": "36氪获悉，12月12日，布瑞克首届“农产品采购狂欢节”当日17:30销售额达70692822 元，预计全天销售额将突破亿元。" }, "route": "detail_newsflash?itemId=1007544256052737" }, { "itemId": 1007525970984708, "itemType": 20, "templateMaterial": { "itemId": 1007525970984708, "templateType": 0, "widgetImage": "https://img.36krcdn.com/20201212/v2_14f025d6038140df89f5780941462274_img_jpeg", "publishTime": 1607766505064, "widgetTitle": "华海顺达称将禁止给“严重低价”社区团购平台供货", "widgetContent": "36氪获悉，12月12日，沧州市华海顺达粮油调料有限公司发布“关于禁止给社区团购平台供货公司供货通知”，该公司称，公司收到多方投诉，以多多买菜、美团优选等位代表的社区团购平台出现严重低价现象，甚至个别产品远低于出厂价，影响严重，损害客户利益，现针对经销商操作社区团购平台做出以下要求。" }, "route": "detail_newsflash?itemId=1007525970984708" }, { "itemId": 1007518222728709, "itemType": 20, "templateMaterial": { "itemId": 1007518222728709, "templateType": 0, "publishTime": 1607766032148, "widgetTitle": "一汽-大众：任命潘占福为总经理、党委书记，刘亦功不再兼任", "widgetContent": "36氪获悉，据一汽官网消息，2020年12月12日下午，一汽-大众公司召开干部会议。集团公司领导徐留平、邱现东、秦焕明、刘亦功出席。会议宣布：经集团公司党委常委会研究决定，刘亦功同志不再兼任一汽-大众汽车有限公司总经理、党委书记；潘占福同志任一汽-大众汽车有限公司总经理、党委书记；董修惠同志任集团公司合资合作事业管理部副总经理（主持工作）；郭永锋同志任一汽-大众副总经理兼一汽-大众销售有限责任公司总经理、党委书记。" }, "route": "detail_newsflash?itemId=1007518222728709" }, { "itemId": 1007480201920006, "itemType": 20, "templateMaterial": { "itemId": 1007480201920006, "templateType": 0, "publishTime": 1607763711542, "widgetTitle": "法国监管机构对谷歌和亚马逊开出1.35亿欧元罚单", "widgetContent": "12月10日法国监管机构宣布，对美国谷歌公司及其下属企业和亚马逊公司分别处以1亿欧元和3500万欧元的罚款，理由是这两家互联网企业未经同意搜集用户上网痕迹。（澎湃新闻）", "sourceUrlRoute": "webview?url=https%3A%2F%2Fwww.thepaper.cn%2FnewsDetail_forward_10374010" }, "route": "detail_newsflash?itemId=1007480201920006" }, { "itemId": 1007478665477888, "itemType": 20, "templateMaterial": { "itemId": 1007478665477888, "templateType": 0, "publishTime": 1607763617765, "widgetTitle": "爱心小熊全球首店落地上海，设总面积1500平方米体验中心", "widgetContent": "12月12日，全球第一家爱心小熊线下沉浸式体验中心——kalidico奇幻研究所，正式落地上海北外滩的浦西第一高楼白玉兰广场，爱心小熊Care Bears诞生于美国，是一个有着近40年历史的全球化潮流ICON（图标）。（澎湃新闻）", "sourceUrlRoute": "webview?url=https%3A%2F%2Fwww.thepaper.cn%2FnewsDetail_forward_10374104" }, "route": "detail_newsflash?itemId=1007478665477888" }, { "itemId": 1007474885426689, "itemType": 20, "templateMaterial": { "itemId": 1007474885426689, "templateType": 0, "publishTime": 1607763387049, "widgetTitle": "全国首单电商平台数字人民币消费产生", "widgetContent": "36氪获悉，12月11日20时00分02秒，全国首单电商平台数字人民币消费诞生，苏州的一位消费者在京东商城成功下单。" }, "route": "detail_newsflash?itemId=1007474885426689" }, { "itemId": 1007474408783619, "itemType": 20, "templateMaterial": { "itemId": 1007474408783619, "templateType": 0, "publishTime": 1607763357957, "widgetTitle": "长虹虹魔方与酷狗音乐、爱听卓乐宣布达成合作", "widgetContent": "36氪获悉，12月12日，长虹虹魔方与酷狗音乐、爱听卓乐宣布达成合作，通过卓乐云·智能电视音乐全生态解决方案，三方将携手推动智能电视音娱服务的优化与升级，同时，长虹正式推出了全球首台5G+AIoT全娱生态极智屏电视Q8T PRO，开启音乐与大屏融合下的极智屏3.0时代。" }, "route": "detail_newsflash?itemId=1007474408783619" }, { "itemId": 1007421930897155, "itemType": 20, "templateMaterial": { "itemId": 1007421930897155, "templateType": 0, "publishTime": 1607760154961, "widgetTitle": "美团优选通报首个贪腐案，原陕宁省区负责人被刑拘", "widgetContent": "36氪获悉，12月12 日，美团在内部最新通报了一起反腐案件，美团优选陕宁（陕西、宁夏）省区负责人马军，因受贿已被西安警方刑事拘留。该案件在美团内部被定义为“优选首案”，是美团优选业务自今年 7 月成立以来，首个内部通报的违规违法案例。在内部信中，美团称：优选业务起步不久，业务模式新、员工新，更需要重视廉正问题，对贪腐舞弊行为“零容忍”。", "sourceUrlRoute": "webview?url=https%3A%2F%2F36kr.com%2Fp%2F1007281304370695" }, "route": "detail_newsflash?itemId=1007421930897155" }, { "itemId": 1007420671491840, "itemType": 20, "templateMaterial": { "itemId": 1007420671491840, "templateType": 0, "publishTime": 1607760078093, "widgetTitle": "格力集团与澳门科协达成合作，将共建珠澳产业型科技馆项目", "widgetContent": "36氪获悉，格力集团与澳门科学技术协进会已于12月10日签署《战略合作框架协议书》，共同建设运营珠澳产业型科技馆项目。根据协议内容，珠澳产业型科技馆计划落地在由格力集团投资打造的珠海三溪科创小镇启动区首期项目“格创·集城”内，拟打造“科技产品全产业链条服务平台”，将规划创新科技项目孵化及实践、科技产品展销、科普教育体验、科普机构开发运营服务供应等四大功能板块。", "sourceUrlRoute": "webview?url=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FQ56xxicM80F-mvxZW3pOAw" }, "route": "detail_newsflash?itemId=1007420671491840" }, { "itemId": 1007419330772739, "itemType": 20, "templateMaterial": { "itemId": 1007419330772739, "templateType": 0, "publishTime": 1607759996262, "widgetTitle": "特斯拉团队下月将访印尼，拟建设电池工厂", "widgetContent": "印尼政府周六在一份声明中表示，美国汽车制造商特斯拉将于下月派代表团前往印尼，讨论对其电动汽车供应链的潜在投资。马斯克表示，只要镍的开采“高效且环保”，他计划提供一份“长期的巨额合同”。（路透社）" }, "route": "detail_newsflash?itemId=1007419330772739" }, { "itemId": 1007417730383361, "itemType": 20, "templateMaterial": { "itemId": 1007417730383361, "templateType": 0, "publishTime": 1607759898582, "widgetTitle": "豌豆思维与清华大学出版社达成教材合作", "widgetContent": "36氪获悉，12月12日，在线小班课行业领先的豌豆思维与清华大学出版社达成战略合作，双方将共同出版《少儿思维丛书》，为中国2-12岁的孩子提供专业权威的思维启蒙类教材，并在现场签署了战略合作协议。同时，豌豆思维还将与清华大学相关院系、清华大学未来实验室，共同探索儿童数理思维启蒙方面合作，共同推动中国数理思维人才的培养。" }, "route": "detail_newsflash?itemId=1007417730383361" }, { "itemId": 1007345127341573, "itemType": 20, "templateMaterial": { "itemId": 1007345127341573, "templateType": 0, "publishTime": 1607755467244, "widgetTitle": "苏宁双12半天战报：手机以旧换新同比翻两番 iPhone12换新占比65%", "widgetContent": "36氪获悉，苏宁易购大数据显示，截至12日12点，苏宁易购手机以旧换新活动同比增长200%，一站式以旧换新占比73%。" }, "route": "detail_newsflash?itemId=1007345127341573" }, { "itemId": 1007344115416581, "itemType": 20, "templateMaterial": { "itemId": 1007344115416581, "templateType": 0, "publishTime": 1607755405481, "widgetTitle": "道富、瑞银正就合并资产管理业务进行谈判", "widgetContent": "据知情人士透露，道富和瑞银两家公司正在就合并资产管理业务进行谈判。知情人士称，这两家公司自2020年初以来一直在进行讨论，到今年夏天似乎接近达成协议。彭博新闻社早前报道称，道富决定权衡资产管理业务的各种选择，包括与瑞银或另一竞争对手合并。（华尔街日报）" }, "route": "detail_newsflash?itemId=1007344115416581" }, { "itemId": 1007343522103041, "itemType": 20, "templateMaterial": { "itemId": 1007343522103041, "templateType": 0, "publishTime": 1607755369268, "widgetTitle": "茅台习酒今年销售额破百亿，明年目标锁定120亿", "widgetContent": "12月12日，茅台集团习酒公司2021年全国经销商大会在浙江杭州召开。记者从会上获悉，2020年习酒销售额实现破百亿目标，整体销售额同比增长31.29%，提前超额完成年度目标任务，销售业绩突破历史新高。此外，2021年习酒规划目标为：含税销售额120亿元，成品酒计划销售3.2万吨，省外市场销售额达到90亿元，占比达到75%；高端产品实现78亿元，占比超过65%。（微酒）" }, "route": "detail_newsflash?itemId=1007343522103041" }, { "itemId": 1007265759592200, "itemType": 20, "templateMaterial": { "itemId": 1007265759592200, "templateType": 0, "publishTime": 1607750623021, "widgetTitle": "南京：住房租赁企业不得诱导、强迫租客使用租金贷", "widgetContent": "据南京住房保障和房产局网站12月12日消息，南京市住房保障和房产局、南京市发展和改革委员会、南京市公安局等八部门联合发布《关于进一步加强全市住房租赁市场监管 规范市场秩序的通知》提出，严禁住房租赁企业等相关主体通过自办金融或与其他机构合作，为租房违规加杠杆提供产品和服务。住房租赁企业等相关主体不得以租金分期、租金优惠等名义诱导、隐瞒、欺骗或强迫要求承租人使用“租金贷”。（界面新闻）", "sourceUrlRoute": "webview?url=https%3A%2F%2Fwww.jiemian.com%2Farticle%2F5394924.html" }, "route": "detail_newsflash?itemId=1007265759592200" }, { "itemId": 1007250855427588, "itemType": 20, "templateMaterial": { "itemId": 1007250855427588, "templateType": 0, "publishTime": 1607749713343, "widgetTitle": "苏宁iPhone12以旧换新补贴加码，最低补贴700元", "widgetContent": "苏宁易购宣布，自12日0点起，推出总额10亿元的“超级双十二补贴”，用户登陆苏宁易购APP即可享受补贴。自12日0点起，iPhone12新品以旧换新补贴加码，用户通过苏宁易购以旧换新购买iPhone12新机，除了旧机抵扣金额外，还可获得最高1500元的额外补贴。据悉，此次苏宁易购iPhone12新品以旧换新补贴加码，范围涵盖iPhone12、iPhone12mini等产品，用户旧机价值满300元即可获得700元补贴，旧机价值满2000元额外补贴1000元，旧机价值满5000元额外补贴1500元。（中证网）" }, "route": "detail_newsflash?itemId=1007250855427588" }, { "itemId": 1007173817188099, "itemType": 20, "templateMaterial": { "itemId": 1007173817188099, "templateType": 0, "publishTime": 1607745011302, "widgetTitle": "中国慕课数量及应用规模已居世界第一", "widgetContent": "北京召开的世界慕课大会宣布，中国慕课数量与学习规模已位居世界第一。慕课，即大规模在线开放课程，是信息技术与教育教学深度融合的结晶。中国慕课自2013年起步，从“建、用、学、管”等多个层面全面推进，目前上线慕课数量超过3.4万门，学习人数达5.4亿人次。（新浪财经）" }, "route": "detail_newsflash?itemId=1007173817188099" }, { "itemId": 1007173005229574, "itemType": 20, "templateMaterial": { "itemId": 1007173005229574, "templateType": 0, "publishTime": 1607744961744, "widgetTitle": "《赛博朋克2077》1天内盈利，B站或成中国代理", "widgetContent": "36氪获悉，根据CDPR官方发布的报告，《赛博朋克2077》的预购量和首发日销量已经超过了其巨大的投入和市场宣传费用。也就是说，《赛博朋克2077》仅用一天的时间就已经回本和盈利了。《赛博朋克2077》是知名游戏《巫师》系列开发商波兰公司CD Projekt RED开发制作的一款角色扮演游戏，于12月10日正式上线。此前，《赛博朋克2077》中文情报站在哔哩哔哩（B站）上线，并开启预约，市场猜测B站或成为《赛博朋克2077》中国代理。" }, "route": "detail_newsflash?itemId=1007173005229574" }, { "itemId": 1007171959045894, "itemType": 20, "templateMaterial": { "itemId": 1007171959045894, "templateType": 0, "publishTime": 1607744897890, "widgetTitle": "国家邮政局：前11个月，全国快递服务企业业务量累计完成741亿件，同比增长30.5%", "widgetContent": "36氪获悉，据“国家邮政局”微信公众号，1-11月，邮政行业业务收入（不包括邮政储蓄银行直接营业收入）累计完成9928.5亿元，同比增长14.4%；业务总量累计完成18752.9亿元，同比增长29.2%。1-11月，全国快递服务企业业务量累计完成741亿件，同比增长30.5%；业务收入累计完成7869.2亿元，同比增长17.0%。", "sourceUrlRoute": "webview?url=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FkmhMWB_R2Y1mBgm7afS8Mw" }, "route": "detail_newsflash?itemId=1007171959045894" }, { "itemId": 1007170576596488, "itemType": 20, "templateMaterial": { "itemId": 1007170576596488, "templateType": 0, "publishTime": 1607744813512, "widgetTitle": "特朗普称第一批新冠疫苗将在24小时内投入使用", "widgetContent": "特朗普称第一批新冠疫苗将在24小时内投入使用。(财联社)" }, "route": "detail_newsflash?itemId=1007170576596488" }], "pageCallback": "eyJmaXJzdElkIjoxMDA3NTQ0MjU2MDUyNzM3LCJsYXN0SWQiOjEwMDcxNzA1NzY1OTY0ODgsImZpcnN0Q3JlYXRlVGltZSI6MTYwNzc2NzYyMTA5NiwibGFzdENyZWF0ZVRpbWUiOjE2MDc3NDQ4MTM1MTJ9", "hasNextPage": 1 } }, "hotlist": { "code": 0, "data": [{ "itemId": 995607580251139, "itemType": 10, "templateMaterial": { "itemId": 995607580251139, "templateType": 3, "widgetImage": "https://img.36krcdn.com/20201204/v2_382bb379676f40819a597365084ce0f5_img_jpg?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center", "publishTime": 1607667865998, "widgetTitle": "36氪独家丨阿里核心电商组织架构大调整：汤兴全面负责淘系产品技术，吹雪全面负责天猫运营" }, "route": "detail_article?itemId=995607580251139" }, { "itemId": 1006000817110024, "itemType": 10, "templateMaterial": { "itemId": 1006000817110024, "templateType": 3, "widgetImage": "https://img.36krcdn.com/20201211/v2_f5f9ebac79a8403d96e531aa93237da5_img_jpeg?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center", "publishTime": 1607677831841, "widgetTitle": "深氪 | 泡泡玛特融资故事：得到的、错过的，以及得到又错过的" }, "route": "detail_article?itemId=1006000817110024" }, { "itemId": 1007281304370695, "itemType": 10, "templateMaterial": { "itemId": 1007281304370695, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20201212/v2_56c4fa993b544074b14c46d5ba41fd04_img_png?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center", "publishTime": 1607757641401, "widgetTitle": "36氪独家 | 美团优选通报首个贪腐案，原陕宁省区负责人被刑拘" }, "route": "detail_article?itemId=1007281304370695" }, { "itemId": 1006119305346568, "itemType": 10, "templateMaterial": { "itemId": 1006119305346568, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20201211/v2_b2b8d9cb50f74b78a3a5130c6740c3a4_img_jpg?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center", "publishTime": 1607681082702, "widgetTitle": "人民日报评论社区团购：流量变现以外，巨头应承担起科技创新的责任" }, "route": "detail_article?itemId=1006119305346568" }, { "itemId": 1005665332061705, "itemType": 10, "templateMaterial": { "itemId": 1005665332061705, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20201211/v2_88c346941b274902a5784f660e4abf6c_img_jpg?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center", "publishTime": 1607659710000, "widgetTitle": "今天，33岁创始人IPO敲钟：泡泡玛特市值1000亿" }, "route": "detail_article?itemId=1005665332061705" }, { "itemId": 1006360673025536, "itemType": 10, "templateMaterial": { "itemId": 1006360673025536, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20201211/v2_bc68004eb343446d8befb1ceb2a3eba5_img_jpeg?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center", "publishTime": 1607733481155, "widgetTitle": "最前线｜京东“偷袭珍珠港”，战略投资兴盛优选7亿美金" }, "route": "detail_article?itemId=1006360673025536" }, { "itemId": 823504201342080, "itemType": 10, "templateMaterial": { "itemId": 823504201342080, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20200826/v2_e773f37c91b14f2c80b20f6a985ce5f6_img_jpg", "publishTime": 1607684152112, "widgetTitle": "市场大事件丨拼多多上线“多多钱包”，7亿人都可以用的第三方支付" }, "route": "detail_article?itemId=823504201342080" }, { "itemId": 1005765833895177, "itemType": 10, "templateMaterial": { "itemId": 1005765833895177, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20201211/v2_410bb2622d054c94957cdb586f6a73d4_img_png", "publishTime": 1607659545679, "widgetTitle": "探秘辛巴燕窝大本营，糖水在这里变燕窝" }, "route": "detail_article?itemId=1005765833895177" }, { "itemId": 1006343270383368, "itemType": 10, "templateMaterial": { "itemId": 1006343270383368, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20201211/v2_c74e7257f4a3427ab0ec2a3c8bcf621d_img_jpeg", "publishTime": 1607731200913, "widgetTitle": "36氪独家 | 智能养生科技品牌「左点」获过亿元A+轮融资，高瓴创投领投" }, "route": "detail_article?itemId=1006343270383368" }, { "itemId": 1006909913677312, "itemType": 10, "templateMaterial": { "itemId": 1006909913677312, "templateType": 1, "widgetImage": "https://img.36krcdn.com/20201212/v2_ac5051ad36944856b54a7c2a41a8d397_img_jpeg?x-oss-process=image/resize,m_mfit,w_600,h_400,limit_0/crop,w_600,h_400,g_center", "publishTime": 1607731982000, "widgetTitle": "9点1氪 | 新能源汽车市场明年增速或超30%；阿里启动AIOT伙伴计划；新冠疫苗试验最终疗效结果显示95%有效率" }, "route": "detail_article?itemId=1006909913677312" }] } } }, "channel": [{ "id": 0, "key": "web_news", "name": "最新", "mark": "none", "route": "nav_latest?subnavNick=web_news&subnavType=1" }, { "id": 1, "key": "web_recommend", "name": "推荐", "mark": "none", "route": "nav_general?subnavNick=web_recommend&subnavType=1" }, { "id": 2, "key": "contact", "name": "创投", "mark": "none", "route": "nav_general?subnavNick=contact&subnavType=1" }, { "id": 3, "key": "ccs", "name": "Markets", "mark": "none", "route": "nav_general?subnavNick=ccs&subnavType=1" }, { "id": 4, "key": "travel", "name": "汽车", "mark": "none", "route": "nav_general?subnavNick=travel&subnavType=1" }, { "id": 5, "key": "technology", "name": "科技", "mark": "none", "route": "nav_general?subnavNick=technology&subnavType=1" }, { "id": 6, "key": "enterpriseservice", "name": "企服", "mark": "none", "route": "nav_general?subnavNick=enterpriseservice&subnavType=1" }, { "id": 7, "key": "banking", "name": "金融", "mark": "none", "route": "nav_general?subnavNick=banking&subnavType=1" }, { "id": 8, "key": "happy_life", "name": "生活", "mark": "none", "route": "nav_general?subnavNick=happy_life&subnavType=1" }, { "id": 9, "key": "innovate", "name": "创新", "mark": "none", "route": "nav_general?subnavNick=innovate&subnavType=1" }, { "id": 10, "key": "real_estate", "name": "房产", "mark": "none", "route": "nav_general?subnavNick=real_estate&subnavType=1" }, { "id": 11, "key": "web_zhichang", "name": "职场", "mark": "none", "route": "nav_general?subnavNick=web_zhichang&subnavType=1" }, { "id": 12, "key": "member", "name": "会员", "mark": "none", "route": "nav_general?subnavNick=member&subnavType=1" }, { "id": 13, "key": "other", "name": "其他", "mark": "none", "route": "nav_general?subnavNick=other&subnavType=1" }], "locationChannel": [{ "id": 0, "key": "guangdong", "name": "广东", "route": "nav_station?subnavNick=guangdong&subnavType=2" }, { "id": 1, "key": "jiangsu", "name": "江苏", "route": "nav_station?subnavNick=jiangsu&subnavType=2" }, { "id": 2, "key": "sichuan", "name": "四川", "route": "nav_station?subnavNick=sichuan&subnavType=2" }, { "id": 3, "key": "qingdao", "name": "山东", "route": "nav_station?subnavNick=qingdao&subnavType=2" }, { "id": 4, "key": "liaoning", "name": "辽宁", "route": "nav_station?subnavNick=liaoning&subnavType=2" }, { "id": 5, "key": "nanchang", "name": "南昌", "route": "nav_station?subnavNick=nanchang&subnavType=2" }, { "id": 6, "key": "hainan", "name": "海南", "route": "nav_station?subnavNick=hainan&subnavType=2" }, { "id": 7, "key": "zhejiang", "name": "浙江", "route": "nav_station?subnavNick=zhejiang&subnavType=2" }, { "id": 8, "key": "xian", "name": "陕西", "route": "nav_station?subnavNick=xian&subnavType=2" }, { "id": 9, "key": "chongqing", "name": "重庆", "route": "nav_station?subnavNick=chongqing&subnavType=2" }, { "id": 10, "key": "hunan", "name": "湖南", "route": "nav_station?subnavNick=hunan&subnavType=2" }, { "id": 11, "key": "guizhou", "name": "贵州", "route": "nav_station?subnavNick=guizhou&subnavType=2" }], "locationStationNav": "", "userInfo": null, "isCheckedUserInfo": false }</script>
            <script src="//static.36krcdn.com/36kr-web/static/runtime.703c1f0f.js" type="text/javascript"></script>
            <script src="//static.36krcdn.com/36kr-web/static/app.73ec8386.js" type="text/javascript"></script>
        </body>
        """

        """

        """
