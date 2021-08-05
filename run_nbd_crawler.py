# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-19 14:39:55
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-20 11:59:20

from Crawlers.crawler_nbd import nbdStockCrawler

if __name__ == '__main__':
    web_crawl_obj = nbdStockCrawler(10, ThreadsNum=1, IP='localhost',\
                        PORT=27017, dbName='NBD_Stock', collectionName='nbd_news_company')
    web_crawl_obj.coroutine_run()