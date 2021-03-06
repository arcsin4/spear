# -*- coding: utf-8 -*-

from core.crawler.crawl_sseinfo import CrawlSseinfo
from core.crawler.crawl_cninfo import CrawlCninfo
from core.crawler.crawl_cnstock import CrawlCnstock
from core.crawler.crawl_cs import CrawlCs
from core.crawler.crawl_36kr import Crawl36kr
from core.crawler.crawl_thepaper import CrawlThepaper
from core.crawler.crawl_yicai import CrawlYicai
from core.crawler.crawl_ijiwei import CrawlIjiwei
from core.crawler.crawl_cctv import CrawlCctv
from core.crawler.crawl_gov import CrawlGov

__all__ = [
    "CrawlSseinfo",
    "CrawlCninfo",
    "CrawlCnstock",
    "CrawlCs",
    "Crawl36kr",
    "CrawlThepaper",
    "CrawlYicai",
    "CrawlIjiwei",
    "CrawlCctv",
    "CrawlGov",
]