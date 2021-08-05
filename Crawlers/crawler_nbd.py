# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-19 14:39:24
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-21 17:12:59

import re, requests, time, datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient

from textProcessing.processingArticle import processArticle

import gevent
from gevent import monkey
monkey.patch_all()

class nbdStockCrawler(object):
    '''Crawl company news from 'http://stocks.nbd.com.cn/columns/275' website.

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
        self.totalPages = arg[0]
        #self.Range = arg[1]
        self.ThreadsNum = kwarg['ThreadsNum']
        self.IP = kwarg['IP']
        self.PORT = kwarg['PORT']
        self.dbName = kwarg['dbName']
        self.colName = kwarg['collectionName']

    def ConnDB():
        '''
        Connect to mongodb datebase
        '''
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

    def getInfo_fromNbd(self, url_specific:str)->(str, str):
        '''
        Analyze the specified news page and get the release date and Chinese only content
        '''
        resp = requests.get(url_specific)
        date, article = '', ''
        if resp.status_code == 200:
            bs = BeautifulSoup(resp.text, 'lxml')
            #find date
            date = bs.find('span', class_='time', text=True).text
            date = re.sub('\n', '', date)
            date.strip()



            #find article
            content = bs.find('div', class_='g-articl-text')
            p_list = content.find_all('p', style=None, text=True)
            for p in p_list:
                article += p.text
            article = processArticle.regularPro(article)

        return date, article


    def getCompNews_nbd(self):
        '''
        Crawl company news form target web
        (http://stocks.nbd.com.cn/)
        '''
        self.ConnDB()
        AddressList = self.extractDate(['Address'])[0]
        url_stocks = r'http://stocks.nbd.com.cn/'

        if not AddressList:
            nbdStock_browser = webdriver.Chrome()
            surplus_nums = (self.totalPages-1)*15
            nbdStock_browser.get(url_stocks)
            print('Now get information from {}'.format(urlPart))
            while surplus_nums > 0:
                find_more = cnstock_browser.find_element_by_id('more')
                find_more.click()
                time.sleep(1)
                surplus_nums -= 15

            nbdstock_bs = BeautifulSoup(nbdStock_browser.page_source, 'lxml')
            a_list = nbdstock_bs.find_all('a', class_='f-title', target='_blank', text=True)
            nbdStock_browser.close()
            for a in a_list:
                date, article = self.getInfo_fromNbd(a['href'])
                if date and article:
                    data = {'Date' : date,
                            'Address' : a['href'],
                            'Title' : a.text,
                            'Article' : article}
                    self._collection.insert_one(data)

        else:
            nbdStock_browser = webdriver.Chrome()
            surplus_nums = (self.totalPages-1)*15
            nbdStock_browser.get(url_stocks)
            print('Now get information from {}'.format(urlPart))
            while surplus_nums > 0:
                find_more = cnstock_browser.find_element_by_id('more')
                find_more.click()
                time.sleep(1)
                surplus_nums -= 15

            nbdstock_bs = BeautifulSoup(nbdStock_browser.page_source, 'lxml')
            a_list = nbdstock_bs.find_all('a', class_='f-title', target='_blank', text=True)
            nbdStock_browser.close()
            for a in a_list:
                if a['href'] not in AddressList:
                    date, article = self.getInfo_fromNbd(a['href'])
                    if date and article:
                        data = {'Date' : date,
                            'Address' : a['href'],
                            'Title' : a.text,
                            'Article' : article}
                        self._collection.insert_one(data)

    def getCompNews_nbdToday(self):
        self.ConnDB()
        AddressList = self.extractDate(['Address'])[0]
        url_stocks = r'http://stocks.nbd.com.cn/columns/275'
        today = datetime.date.today()
        today= datetime.date.strftime(today, '%Y-%m-%d')

        resp = requests.get(url_stocks)
        resp.encoding = BeautifulSoup(resp.content, 'lxml').original_encoding
        bs = BeautifulSoup(resp.text, 'lxml')
        div_list = bs.find('div', class_='g-list-text').find_all('div', class_='m-list')
        
        for div in div_list:
            if div.find('p' class_='u-channeltime').text and today in div.find('p' class_='u-channeltime').text:
                a_list = div.find_all('a', target='_blank')
                break

        for a in a_list:
            if a['href'] not in AddressList:
                date, article = self.getInfo_fromNbd(a['href'])
                if date and article:
                    data = {'Date' : date,
                        'Address' : a['href'],
                        'Title' : a.text,
                        'Article' : article}
                    self._collection.insert_one(data)


    def coroutine_run(self):
        '''Coroutines running'''
        jobs = []
        jobs.appennd(gevent.spawn(self.getCompNews_nbd))
        gevent.joinall(jobs)