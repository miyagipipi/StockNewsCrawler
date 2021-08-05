# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-14 16:15:48
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-29 22:19:05

import re
import requests
from bs4 import BeautifulSoup
import time, datetime
from selenium import webdriver

from pymongo import MongoClient

import gevent
from gevent import monkey
monkey.patch_all

class CnstockCrawler(object):
    '''Crawl company news from 
    'http://company.cnstock.com/company/scp_gsxw/',
    'http://ggjd.cnstock.com/gglist/search/qmtbbdj/',
    'http://ggjd.cnstock.com/gglist/search/ggkx/' website.

    # Arguments:
        totalPages: Number of pages set to be crawled.
        ThreadsNum: Number of threads needed to be start.
        dbName: Name of database.
        colName: Name of collection.
        IP: Local IP address.
        PORT: Port number corresponding to IP address.
    '''
    def __init__(self,IP:str,PORT:int,dbName:str,collectionName:str, ThreadsNum=1):
        super(CnstockCrawler, self).__init__()
        self.ThreadsNum = ThreadsNum
        self.IP = IP
        self.PORT = PORT
        self.dbName = dbName
        self.colName = collectionName

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

'''
    因为URL采用了JS动态加载，所以传统翻页已经无效，
    不再需要getPageList函数来处理每一页的数字

    def getPageList(self, totalPages:int, Range:int, startPage:int)->list:
        
        Generating a page number list contained totalPages from startPage,
        the size of every element are 'Range'

        pageList = []
        k = startPage

        while k+Range-1 <= totalPages:
            pageList.append((k, k+Range-1))
            k += Range
            if k+Range-1 == totalPages:
                return pageList

        if k+Range-1 > totalPages:
            return pageList.append((k, totalPages))
'''


    def getCompNews_Cnstock(self, totalPages:int, urlPart:str):
        self.ConnDB()
        AddressList = self.extractDate(['Address'])[0]
        if not AddressList:#当数据库中不存在任何地址值时
            cnstock_browser = webdriver.Chrome()
            surplus_pages = totalPages - 20
            cnstock_browser.get(urlPart)
            print('Now get information from {}'.format(urlPart))
            while surplus_pages > 0:
                find_more = cnstock_browser.find_element_by_id('j_more_btn')
                find_more.click()
                time.sleep(1)
                surplus_pages -= 10
            
            cnstock_bs = BeautifulSoup(cnstock_browser.page_source, 'lxml')
            cn_a = cnstock_bs.find_all('a', href = re.compile(r"https://company.cnstock.com/company/scp_.*htm$"), \
                target='_blank', text=True)
            cnstock_browser.close()
            for a in cn_a:
                date, article = self.getUrlInfo(a['href'])
                if article:
                    data = {'Date': date,
                            'Address': a['href'],
                            'Title': a['title'],
                            'Article': article}
                    self._collection.insert_one(data)

        else:
            cnstock_browser = webdriver.Chrome()
            surplus_pages = totalPages - 20
            cnstock_browser.get(urlPart)
            print('Now get information from {}'.format(urlPart))
            while surplus_pages > 0:
                find_more = cnstock_browser.find_element_by_id('j_more_btm')
                find_more.click()
                time.sleep(1)
                surplus_pages -= 10

            cnstock_bs = BeautifulSoup(cnstock_browser.page_source, 'lxml')
            cn_a = cnstock_bs.find_all('a', href = re.compile(r"https://company.cnstock.com/company/scp_.*htm$"), \
                target='_blank', text=True)
            cnstock_browser.close()
            for a in cn_a:
                if a['href'] not in AddressList:
                    date, article = self.getUrlInfo(a['href'])
                    if article:
                        data = {'Date': date,
                                'Address': a['href'],
                                'Title': a['title'],
                                'Article': article}
                        self._collection.insert_one(data)

    def getCompNews_CnToday(self, url_body:str):
        self.ConnDB()
        AddressList = self.extractDate(['Address'])[0]
        today_str = datetime.date.strftime(datetime.date.today(), '%Y-%m-%d')
        cnstock_browser = webdriver.Chrome()
        cnstock_browser.get(url_body)

        is_last_time = False
        bs = BeautifulSoup(browser.page_source, 'lxml')
        spans = bs.find('div', class_='bd').find_all('span', class_='time', text=True)
        if len(spans[-1].text) > 5:
            is_last_time = True
        while not is_last_time:
            find_more = cnstock_browser.find_element_by_id('j_more_btm')
            find_more.click()
            time.sleep(1)
            bs = BeautifulSoup(browser.page_source, 'lxml')
            spans = bs.find('div', class_='bd').find_all('span', class_='time', text=True)
            if len(spans[-1].text) > 5:
                is_last_time = True

        cn_a = bs.find('div', class_='bd').find_all('a', href = re.compile(r"https://company.cnstock.com/company/scp_.*htm$"), \
            target='_blank', text=True)

        if not AddressList:
            for a in cn_a:
                date, article = self.getUrlInfo(a['href'])
                if article and date.find(today_str) != -1:
                    data = {'Date': date,
                            'Address': a['href'],
                            'Title': a['title'],
                            'Article': article}
                    self._collection.insert_one(data)
                elif date.find(today_str) == -1:
                    break
        else:
            for a in a_list:
                if a['href'] not in AddressList:
                    date, article = self.getUrlInfo(a['href'])
                    if article and date.find(today_str) != -1:
                        data = {'Date': date,
                                'Address': a['href'],
                                'Title': a['title'],
                                'Article': article}
                        self._collection.insert_one(data)
                    elif date.find(today_str) == -1:
                        break
        cnstock_browser.close()


    def getUrlInfo(self, news_url:str):
        '''
        Analyze the specified news page and get the release date and Chinese only content
        '''
        resp = requests.get(news_url)
        article = ''
        date = ''
        if resp.status_code == 200:
            bs = BeautifulSoup(resp.text, 'lxml')
            #get date
            date = bs.find('span', class_ = 'timer').text

            #get Chinese article
            content_list = bs.find('div', class_='content', id='qmt_content_div').find_all('p')
            space = re.compile(r'\u3000')
            for paragraph in content_list:
                paragraph_text = paragraph.text
                article += paragraph_text
            article = re.sub(space, '', article)

        return date, article

    def coroutine_run(self, totalPages:int, **kwarg):
        '''Coroutine running'''
        jobs = []
        jobs.append(gevent.spawn(self.getCompNews_Cnstock, totalPages, kwarg['url']))
        gevent.joinall(jobs)

#。。。。