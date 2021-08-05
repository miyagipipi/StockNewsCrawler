# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-26 12:51:17
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-26 13:01:24

from pymongo import MongoClient
import jieba
import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class TextCloud(object):
    def __init__(IP, PORT, dbName, collectionName):
        self.IP = IP
        self.PORT = PORT
    
    def ConnDB(self):
        Client = MongoClient(self.IP, self.PORT)
        db = Client[dbName]
        self._collection = db[collectionName]

    def extractDate(self, tagList:list)->list:
        '''Extract column date(the tag in tagList) into a list'''
        data = []
        for tag in tagList:
            res = self._collection.distinct(str(tag))
            data.append(res)
        return data

    def genCloud(self, rawString):
        jieba.analyse.set_stop_words(r'.\StopWords.txt')
        res_analy = jieba.analyse.extract_tags(res_jb, topK=50, withWeight=False, allowPOS=())

        wc = WordCloud(font_path=r'C:\Windows\Fonts\simsun.ttc', width=1800, height=1600,mode='RGBA', background_color=None).generate(' '.join(res_analy))
        plt.imshow(wc)
        plt.axis('off')
        plt.show()