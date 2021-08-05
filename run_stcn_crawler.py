# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-20 15:29:28
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-20 17:07:37
from Crawlers.crawler_sina import stcnStockCrawler

if __name__ == '__main__':
    web_crawl_obj = stcnStockCrawler(20, 5, IP="localhost",PORT=27017,ThreadsNum=4,\
                                    dbName="Stcn_Stock",collectionName="stcn_news_company")
    web_crawl_obj.coroutine_run(0)