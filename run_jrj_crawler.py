# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-18 15:50:13
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-19 14:38:02

from Crawlers.crawler_jrj import jrjStockCrawler

if __name__ == '__main__':
    web_crawl_obj = jrjStockCrawler('2021-01-01', '2021-07-19', 100,\
                        IP='localhost', PORT=27017, ThreadsNum=1,\
                        dbName='Jrj_stock', collectionName='jrj_news_company')