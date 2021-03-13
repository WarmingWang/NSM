# -*- coding: UTF-8 -*-

import re
import os
import sys
import time
import json
import math
import jieba
import random
import codecs
import logging

from collections import Counter, defaultdict
from urllib.request import Request, urlopen

from tqdm import tqdm

from BiliCar.src.utils import utils

logger = logging.getLogger(__name__)  # 操作日志对象
logging.basicConfig(level=logging.ERROR)


class BILI:
    URL_HOME = 'https://api.bilibili.com/x/web-interface/newlist?rid=176&type=0&ps=50'    #汽车区
    car_counter = defaultdict(int)
    with codecs.open(r'..\..\txt\car.txt', 'r', 'utf-8') as f:
        car_list = f.read().split(' 10 n\r\n')  # 获取干净的car_list

    # tongyici_tihuan.txt是同义词表，每行是一系列同义词，用tab分割
    # 1读取同义词表：并生成一个字典。
    combine_dict = {}
    for line in codecs.open(r'..\..\txt\tongyici.txt', 'r', 'utf-8'):
        seperate_word = line.strip().split(" ")
        num = len(seperate_word)
        # print(num)
        for i in range(0, num):
            combine_dict[seperate_word[i].upper()] = seperate_word[0]
    # print(combine_dict)
    # 创建停用词list
    def stopwordslist(self, filepath):
        stopwords = [line.strip() for line in open(filepath, 'r', encoding="utf-8").readlines()]
        return stopwords

    # 对句子进行分词
    def seg_sentence(self, sentence1, sentence2):
        sentence1_seged = jieba.cut(sentence1.strip())
        # stopwords = self.stopwordslist('..\..\stopwords\hit_stopwords.txt')  # 这里加载停用词的路径
        for word in sentence1_seged:
            if word in self.car_list:
                if word in self.combine_dict:
                    word = self.combine_dict[word]
                    self.car_counter[word] += 1
                    return 0
        sentence2_seged = jieba.cut(sentence2.strip())
        for word in sentence2_seged:
            if word in self.car_list:
                if word in self.combine_dict:
                    word = self.combine_dict[word]
                    self.car_counter[word] += 1
                    return 0


    def downLifeCar(self):
        lastpagebvid = []
        curpages = 10000
        curpage = 1
        prepubdate = ''
        while curpage < curpages:
            # if curpage % 5 == 1:
            time.sleep(random.randint(1, 3))
            url = self.URL_HOME + '&pn=' + str(curpage)       #访问汽车区第curpage页的50笔数据
            retJson = utils.get_urlopen(url, 'json')
            # print(retJson)
            if len(retJson) <= 0:
                continue
            curpage += 1
            curpages = math.ceil(retJson['data']['page']['count'] / 50)
            # print(len(retJson['data']['archives']))
            curpagebvid = []
            for j in range(len(retJson['data']['archives'])):
                pubdate = time.strftime("%Y-%m", time.localtime(retJson['data']['archives'][j]['pubdate']))
                if pubdate != prepubdate:
                    prepubdate = pubdate
                    print(pubdate)
                bvid = retJson['data']['archives'][j]['bvid']
                title = retJson['data']['archives'][j]['title']
                desc = retJson['data']['archives'][j]['desc']
                curpagebvid.append(bvid)
                if bvid not in lastpagebvid:
                    self.seg_sentence(title, desc)
            lastpagebvid = curpagebvid
            print(self.car_counter)
            # if pubdate != prepubdate:
            #     prepubdate = pubdate
            #     print(pubdate)
                # print(self.car_counter)
            # break
        print(self.car_counter)

#----
bili = BILI()
bili.downLifeCar()