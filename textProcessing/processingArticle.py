# -*- coding: utf-8 -*-
# @Author: LQS
# @Date:   2021-07-19 13:53:12
# @Last Modified by:   LQS
# @Last Modified time: 2021-07-20 16:50:35

import re

class processArticle(object):
    """docstring for processArticle"""
    def __init__(self,):
        super(processArticle, self).__init__()

    def regularPro(self, article:str)->str:
        pattern = re.compile('\u3000|\n')
        res = re.sub(pattern, '', article)
        return res

    def jrj_own(self, article:str)->str:
        res = self.regularPro(article)
        res = re.sub(r'\.klinehk.*} ?', '', res)
        return res

    def stcn_dateArti(self, date:str, article:str, cut_cont:str):
        re_article = self.regularPro(article)
        re_date = self.regularPro(date)
        cut_cont = self.regularPro(cut_cont)
        re_date = re_date.replace(cut_cont, '')
        re_date = re_date.strip()
        return re_date, re_article