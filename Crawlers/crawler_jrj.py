# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-18 15:49:28
# @Last Modified by:   LQS
# @Last Modified time: 2021-08-05 21:12:57
import requests, re, datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient
from textProcessing.processingArticle import processArticle as pA

import gevent
from gevent import monkey
monkey.patch_all()
class jrjStockCrawler(object):
    '''
    # Arguments:
        totalPages: Number of pages set to be crawled.
        Range: Divide total web pages into totalPages/Range parts 
               for multi-threading processing.
        ThreadsNum: Number of threads needed to be start.
        dbName: Name of database.
        colName: Name of collection.
        IP: Local IP address.
        PORT: Port number corresponding to IP address.
    '''
    def __init__(self, *arg, **kwarg):
        super(jrjStockCrawler, self).__init__()
        self.startDate = arg[0]
        self.endDate = arg[1]
        self.Range = arg[2]
        self.ThreadsNum = kwarg['ThreadsNum']
        self.IP = kwarg['IP']
        self.PORT = kwarg['PORT']
        self.dbName = kwarg['dbName']
        self.colName = kwarg['_collectionName']

    def ConnDB(self):
        '''
        Connect to mongodb datebase
        '''
        #创建游标，指定数据库，最后指定集合
        Client = MongoClient(self.IP, self.PORT)
        db = Client[self.dbName]
        self._collection = db[self.colName]

    def extractDate(self, tagList:list)->list:
        '''Extract column date(the tag in tagList) into a list'''
        data = []
        for tag in tagList:
            res = self._collection.distinct(str(tag))
            data.append(res)
        return data

    def getEveryDay(self, startDate:str, endDate:str)->list:
        dateList = []
        dateFormat = '%Y-%m-%d'
        startDate = datetime.datetime.strptime(startDate, dateFormat)
        endDate = datetime.datetime.strptime(endDate, dateFormat)
        while startDate <= endDate:
            dateList.append(startDate.strftime(dateFormat))
            startDate += datetime.timedelta(days = 1)
        return dateList

    def getDateList(self)->list:
        '''
        Divide date list into parts using 'self.Range' parameter.
        '''
        dateList = self.getEveryDay(self.startDate, self.endDate)
        dateNums = len(dateList)
        k = 0
        dateRangeList = []

        while k < dateNums:
            if k + self.Range >= dateNums:
                break
            else:
                dateRangeList.append(dateList[k:k+self.Range])
                k += self.Range
        dateRangeList.append(dateList[k:])
        return dateRangeList

    def findPageNums(self, url:str, date:str)-> int:
        '''Find the number of web pages of specific date.
        '''
        resp = requests.get(url)
        bs = BeautifulSoup(resp.text, 'lxml')
        pages = 1
        a_list = bs.find_all('a', href=re.compile(date.replace('-', '')+'_'), target='_self', text=True)
        if a_list:
            pages = len(a_list)
        return pages



    def getUrlInfo_fromjrj(self, url:str, date_specific:str):
        '''get date and article from a specific web.
        '''
        resp = requests.get(url)
        bs = BeautifulSoup(resp.text, 'lxml')
        date = ''
        article = ''
        #notFoundPage = False
        #start get special date from a special website
        spans = bs.find_all('span')
        for span in spans:
            for child in span.children:
                if child == 'jrj_final_date_start':
                    date = span.text.replace('\r', '').replace('\n', '')
                    break
            if date:
                break
        if not date:
            date = date_specific

        #start get article
        article_bs = bs.find('div', class_='texttit_m1')
        if article_bs:
            article = pA.processArticle().jrj_own(article_bs.text)
        
        return (date, article)

    def getCompNews_jrj(self, dateList:list):
        '''
        Crawl company news form target web
        (http://stock.jrj.com.cn/xwk/)
        '''
        self.ConnDB()
        AddressList = self.extractDate(['Address'])[0]
        if not AddressList:
            url_body = 'http://stock.jrj.com.cn/xwk/'
            url_diffPages = '_1.shtml'
            urls_date = []

            for date in dateList:
                url_complete = url_body + date.replace('-', '')[0:6] +\
                    '/' + date.replace('-', '') + url_diffPages
                pageNums = self.findPageNums(url_complete, date)
                for page in range(1, pageNums+1):
                    url_sheet_cur = url_body + date.replace('-', '')[0:6] +\
                        '/'+ date.replace('-', '') + '_{}.shtml'.format(page)
                    '''
                    url_sheet_cur = urls_date.append(url_body + date.replace('-', '')[0:6] +\
                        '/'+ date.replace('-', '') + '_{}.shtml'.format(page))
                    '''
                    urls_date.append((url_sheet_cur, date))

            for (url_specific, date_specific) in urls_date:
                print('ready to get Info from [{0}], the data is *{1}*'.format(url_specific, date_specific))
                resp = requests.get(url_specific)
                bs = BeautifulSoup(resp.text, 'lxml')
                a_list = bs.find_all('a', href=re.compile(r'http://stock\.jrj\.com\.cn.*?(shtml)$'), text=True, target=None)
                for a in a_list:
                    (date, article)= self.getUrlInfo_fromjrj(a['href'], date_specific)
                    if article:
                        data = {'Date': date,
                                'Address': a['href'],
                                'Title': a.text,
                                'Articel': article}
                        self._collection.insert_one(data)
        else:
            url_body = 'http://stock.jrj.com.cn/xwk/'
            url_diffPages = '_1.shtml'
            urls_date = []

            for date in dateList:
                url_complete = url_body + date.replace('-', '')[0:6] +\
                    '/' + date.replace('-', '') + url_diffPages
                pageNums = self.findPageNums(url_complete, date)
                for page in range(1, pageNums+1):
                    url_sheet_cur = urls_date.append(url_body + date.replace('-', '')[0:6] +\
                        '/'+ date.replace('-', '') + '_{}.shtml'.format(page))
                    urls_date.append((url_sheet_cur, date))

            for url_specific, date_specific in urls_date:
                print('ready to get Info from [{0}], the data is *{1}*'.format(url_specific, date_specific))
                resp = requests.get(url_specific)
                bs = BeautifulSoup(resp.text, 'lxml')
                a_list = bs.find_all('a', href=re.compile(r'http://stock\.jrj\.com\.cn.*?(shtml)$'), text=True, target=None)
                for a in a_list:
                    if a['href'] not in AddressList:
                        (date, article)= self.getUrlInfo_fromjrj(a['href'], date_specific)
                        if article:
                            data = {'Date': date,
                                    'Address': a['href'],
                                    'Title': a.text,
                                    'Articel': article}
                            self._collection.insert_one(data)

    def getCmpNews_jrjToday(self):
        today = datetime.date.today()
        today = datetime.date.strftime(today, '%Y-%m-%d')
        self.getCompNews_jrj([today])

    def coroutine_run(self):
        '''
        Coroutines running
        '''
        jobs = []
        dateLists = self.getDateList()
        for dateList in dateLists:
            jobs.appennd(gevent.spawn(self.getCompNews_jrj, dateList))
        gevent.joinall(jobs)