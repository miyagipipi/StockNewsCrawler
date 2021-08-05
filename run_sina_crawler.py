# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-20 13:46:13
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-20 13:50:37

from Crawlers.crawler_sina import sinaStockCrawler

if __name__ == '__main__':
    web_crawl_obj = WebCrawlFromSina(20,10,ThreadsNum=1,IP="localhost",PORT=27017,\
        dbName="Sina_Stock",collectionName="sina_news_company")
    web_crawl_obj.coroutine_run()