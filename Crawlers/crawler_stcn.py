# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-20 15:29:04
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-22 15:29:57

import requests, re, datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient

from textProcessing.processingArticle import processArticle

from gevent import monkey
monkey.patch_all()

class stcnStockCrawler(object):
    '''Crawl company news from 'https://company.stcn.com/' website.

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

    def getPageList(self, initPageID)->list:
        '''Generate page number list using Range parameter.
        '''
        pageList = []
        k = initPageID
        while k + self.Range < self.totalPages:
            pageList.append((k, k+self.Range-1))
            k += self.Range
        if k + self.Range >= self.totalPages:
            pageList.append((k, self.totalPages-1))
        return pageList

    def getInfo_fromStcn(self, url_specific:str):
        '''Analyze website and extract useful information.
        '''
        resp = requests.get(url_specific)
        resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
        bs = BeautifulSoup(resp.text, 'lxml')
        date = ''
        article = ''
        cut_cont = ''
        #find datetime
        date_bs = bs.find('div', class_='info')
        for cut_conts in date_bs.find_all('span'):
            cut_cont += cut_conts.text
        date = date_bs.text

        #find article
        p_list = bs.find('div', id='ctrlfscont').find_all('p', style=None)
        for p in p_list:
            article += p.text
        if date and article:
            date, article = processArticle.stcn_dateArti(date, article, cut_cont)
        return date, article

    def getCompNews_stcn(self, startPage:int, endPage:int, onlyToday=False):
        '''Crawl historical company news from startPage to endPage
        '''
        if onlyToday:
            today = datetime.date.today()
            today = datetime.date.strftime(today, '%Y-%m-%d')
        url_body = r'https://company.stcn.com/'
        url_index = 'index'
        url_tail = r'.html'
        self.ConnDB()
        AddressList = self.extractDate(['Address'])[0]
        if AddressList:
            urls = []
            for pageID in range(startPage, endPage+1):
                if pageID == 0:
                    url_complete = url_body + url_index + url_tail
                else:
                    url_complete = url_body + url_index + '_{}'.format(pageID) + url_tail
                urls.append(url_complete)
            for url_complete in urls:
                resp = requests.get(url_complete)
                resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
                bs = BeautifulSoup(resp.text, 'lxml')
                div = bs.find('div', class_='box_left')
                a_list = div.find_all('a', target='_blank', title=True, text=True, href=re.compile(r'\.html$'))
                for a in a_list:
                    if a['href'].find('.') != 0:
                        date, article = self.getInfo_fromStcn(a['href'])
                    else:
                        date,article = self.getInfo_fromStcn(url_body+a['href'][1:])
                    if (not onlyToday) and article:
                        data = {'Date' : date,
                                'Address' : a['href'],
                                'Title' : a['title'],
                                'Article' : article}
                        self._collection.insert_one(data)
                    elif onlyToday and article:
                        if today in date:
                            data = {'Date' : date,
                                    'Address' : a['href'],
                                    'Title' : a['title'],
                                    'Article' : article}
                            self._collection.insert_one(data)

        else:
            urls = []
            for pageID in range(startPage, endPage):
                if pageID == 0:
                    url_complete = url_body + url_index + url_tail
                else:
                    url_complete = url_body + url_index + '_{}'.format(pageID) + url_tail
                urls.append(url_complete)
            for url_complete in urls:
                resp = requests.get(url_complete)
                resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
                bs = BeautifulSoup(resp.text, 'lxml')
                div = bs.find('div', class_='box_left')
                a_list = div.find_all('a', target='_blank', title=True, text=True, href=re.compile(r'\.html$'))
                for a in a_list:
                    if a['href'] not in AddressList:
                        if a['href'].find('.') != 0:
                            date, article = self.getInfo_fromStcn(a['href'])
                        else:
                            date,article = self.getInfo_fromStcn(url_body+a['href'][1:])
                        if (not onlyToday) and article:
                            data = {'Date' : date,
                                    'Address' : a['href'],
                                    'Title' : a['title'],
                                    'Article' : article}
                            self._collection.insert_one(data)
                        elif onlyToday and article:
                            if today in date:
                                data = {'Date' : date,
                                        'Address' : a['href'],
                                        'Title' : a['title'],
                                        'Article' : article}
                                self._collection.insert_one(data)

    def getCompNews_stcnToday(self):
        url_body = r'https://company.stcn.com/'
        url_index = 'index'
        url_tail = r'.html'

        today = datetime.date.today()
        today = datetime.date.strftime(today, '%Y-%m-%d')
        startPage = 0
        endPage = 0
        resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
        bs = BeautifulSoup(resp.text, 'lxml')
        while True:
            if endPage == 0:
                resp = requests.get(url_body+url_index+url_tail)
            else:
                resp = requests.get(url_body + url_index + '_{}'.format(endPage) + url_tail)
            resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
            bs = BeautifulSoup(resp.text, 'lxml')
            date_last = bs.find_all('li', style='display: block;')[-1].find('p', class_='sj')
            if today in date_last.text:
                endPage += 1
            else:
                break
        self.getCompNews_stcn(startPage, endPage, onlyToday=True)

    def coroutine_run(self, initPageID, **kwarg):
        '''Coroutines running.
        '''
        jobs = []
        pageRangeList = self.getPageList(initPageID)
        for page_range in pageRangeList:
            jobs.appennd(gevent.spawn(self.getCompNews_stcn, page_range[0], page_range[1], onlyToday=False))
        gevent.joinall(jobs)