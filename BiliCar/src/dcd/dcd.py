# -*- coding: UTF-8 -*-

import re
import os
import sys
import time
import random
import logging

from urllib.request import Request, urlopen

from BiliCar.src.utils import utils

logger = logging.getLogger(__name__)  # 操作日志对象
logging.basicConfig(level=logging.ERROR)


class DCD:

    URL_HOME = 'https://www.dongchedi.com'
    fileCWD = os.path.dirname(os.path.abspath(r".."))

    def saveImg(self, imageURL, picAbsFilename):
        data = utils.get_urlopen(imageURL, 'pic')
        f = open(picAbsFilename, 'wb')
        f.write(data)
        f.close()

    @property
    def downCarLib(self):
        url_carlib = self.URL_HOME + '/auto/library/x-x-x-x-x-x-x-x-x-x-x?'
        i = 0
        while 1:
            try:
                html = utils.get_urlopen(url_carlib, '')
                break
            except:
                i += 1
                if i >= 5:
                    logger.error('访问失败%d次，请检查！', i)
                    return []
                logger.debug('访问失败%d次，1-5秒后尝试再次连接', i)
                time.sleep(random.randint(1, 5))
                continue
        outputs = open(self.fileCWD + '\\txt\\' + 'car.txt', 'w', encoding="utf-8")
        for i in range(ord('A'), ord('Z') + 1):
            cre = re.compile('<div data-letter="'+chr(i)+'" class="jsx-2929075810">(.*?)</div>', re.S)
            html_brand = cre.findall(html)[0]
            # print(html_brand)
            cre = re.compile('<p class="jsx-2929075810 brand brand-(\d+\.?\d*)">.*?<img src="(.*?)".*?<span class="jsx-2929075810">(.*?)</span>', re.S)
            brand = cre.findall(html_brand)
            for per in brand:
                print(per)
                self.saveImg(per[1], self.fileCWD + '\\pic\\' + str(per[0]) + '.jpg')
                outputs.write(per[2] + ' 10 n')
                outputs.write('\n')
        outputs.close()
#----
dcd = DCD()
dcd.downCarLib
