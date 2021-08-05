# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-16 15:11:31
# @Last Modified by:   LQS
# @Last Modified time: 2021-08-05 21:18:46

from Crawlers.crawler_costock import CnstockCrawler

if __name__ == '__main__':
    web_crawl_obj = CnstockCrawler(IP='localhost', PORT=27017, dbName='Cnstock_stock',\
                    collectionName='cnstock_news_company',ThreadsNum=4,)
    web_crawl_obj.coroutine_run(50,url='http://company.cnstock.com/company/scp_gsxw/') #Obj.multi_threads_run()
    #web_crawl_obj.coroutine_run(50,url='http://ggjd.cnstock.com/gglist/search/qmtbbdj/')
    #web_crawl_obj.coroutine_run(50,url='http://ggjd.cnstock.com/gglist/search/ggkx/')
