# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-20 12:00:21
# @Last Modified by:   LQS
# @Last Modified time: 2021-08-05 21:18:47

import requests, re, datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient

from textProcessing.processingArticle import processArticle

import gevent
from gevent import monkey
monkey.patch_all()

class sinaStockCrawler(object):
    '''Crawl company news from 'http://finance.sina.com.cn/roll/index.d.html?cid=56592&page=1' website.

    # Arguments:
        totalPages: Number of pages set to be crawled(int type).
        Range: Divide total web pages into totalPages/Range parts 
               for multi-threading processing(int type).
        ThreadsNum: Number of threads needed to be start(int type).
        dbName: Name of database(string type).
        colName: Name of collection(string type).
        IP: Local IP address(string type).
        PORT: Port number corresponding to IP address(int type).
    '''

    def __init__(self, *arg, **kwarg):
        super(sinaStockCrawler, self).__init__()
        self.totalPages = *arg[0]
        self.Range = *arg[1]
        self.ThreadsNum = kwarg['ThreadsNum']
        self.IP = kwarg['IP']
        self.PORT = kwarg['PORT']
        self.dbName kwarg['dbName']
        self.colName = kwarg['collectionName']

    def ConnDB(self):
        Client = MongoClient(self.IP, self.PORT)
        db = Client[self.dbName]
        self._collection = db[self.colName]

    def extractDate(self, tagList:list)->list:
        date = []
        for tag in tagList:
            res.self._collection.distinct(str(tag))
            date.appennd(res)
        return date

    def getPageList(self)->list:
        '''Generate page number list using Range parameter.
        '''
        pageList = []
        k = 1
        while k + self.Range < self.totalPages:
            pageList.append((k, k+self.Range-1))
            k += self.Range
        if k + self.Range >= self.totalPages:
            pageList.append((k, self.totalPages))
        return pageList

    def getInfo_fromSina(self, url_specific:str):
        resp = requests.get(url_specific)
        resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
        bs = BeautifulSoup(resp.text, 'lxml')
        date, article = '', ''

        #find datetime
        span = bs.find('span', class_='date', text=True)
        if span:
            date = re.sub('年|月', '-', span.text).replace('日', '')

        #find article
        p_list = bs.select("p[cms-style='font-L']")
        for p in p_list[1:-4]:
            article += p.text
        article = processArticle.regularPro(article)
        return date, article

    def getCompNews_sina(self, startPage:int, endPage:int, onlyToday=False):
        '''Crawl historical company news from startPage to endPage
        '''
        self.ConnDB()
        AddressList = self.extractDate(['Address'])[0]
        if onlyToday:
            today = datetime.date.today()
            today = datetime.date.strftime(today, '%Y-%m-%d')
        if not AddressList:
            urls = []
            url_body = r'http://finance.sina.com.cn/roll/index.d.html?cid=56592&page='
            for pageID in range(startPage, endPage+1):
                urls.append(url_body + str(pageID))
            for url_complete in urls:
                resp = requests.get(url_complete)
                resp.encoding = BeautifulSoup(resp.content, "lxml").original_encoding
                bs = BeautifulSoup(resp.text, 'lxml')
                a_list = bs.find_all('a', target='_blank', href=re.compile(r'finance.*?stock.*shtml?'), text=True)
                for a in a_list:
                    date, article = self.getInfo_fromSina(a['href'])
                    if (not onlyToday) and article and date:
                        data = {'Date' : date,
                                'Address' : a['href'],
                                'Title' : a.text,
                                'Article' : article}
                        self._collection.insert_one(data)
                    elif onlyToday and article and date:
                        if today in date:
                            data = {'Date' : date,
                                    'Address' : a['href'],
                                    'Title' : a.text,
                                    'Article' : article}
                        self._collection.insert_one(data)

        else:
            urls = []
            url_body = r'http://finance.sina.com.cn/roll/index.d.html?cid=56592&page='
            for pageID in range(startPage, endPage+1):
                urls.append(url_body + str(pageID))
            for url_complete in urls:
                resp = requests.get(url_complete)
                resp.encoding = BeautifulSoup(resp.content, "lxml").original_encoding
                bs = BeautifulSoup(resp.text, 'lxml')
                a_list = bs.find_all('a', target='_blank', href=re.compile(r'finance.*?stock.*shtml?'), text=True)
                for a in a_list:
                    if a['href'] not in AddressList:
                        date, article = self.getInfo_fromSina(a['href'])
                        if (not onlyToday) and article and date:
                            data = {'Date' : date,
                                    'Address' : a['href'],
                                    'Title' : a.text,
                                    'Article' : article}
                            self._collection.insert_one(data)
                        elif onlyToday and article and date:
                            if today in date:
                                data = {'Date' : date,
                                        'Address' : a['href'],
                                        'Title' : a.text,
                                        'Article' : article}
                                self._collection.insert_one(data)

    def getCompNews_sinaToday(self):
        today = datetime.date.today()
        today = datetime.date.strftime(today, '%m{m}%d{d}').format(m='月', d='日')
        startPage = 1
        endPage = 1
        url_body = r'http://finance.sina.com.cn/roll/index.d.html?cid=56592&page='
        while True:
            url_complete = url_body + str(endPage)
            resp = requests.get(url_complete)
            resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
            bs = BeautifulSoup(resp.text, 'lxml')
            date_last = bs.find_all('ul', class_='list_009')[-1].find_all('li')[-1].find('span', text=True)
            date_tod = re.sub(r'\(|\)', '', date_last.text).strip()
            if today in date_tod:
                endPage += 1
            else:
                break
        self.getCompNews_sina(startPage, endPage, onlyToday=True)


    def coroutine_run(self):
        '''Coroutines running'''
        jobs = []
        pageRangeList = self.getPageList()
        for page_range in pageRangeList:
            jobs.appennd(gevent.spawn(self.getCompNews_sina, page_range[0], page_range[1], onlyToday=False))
        gevent.joinall(jobs)