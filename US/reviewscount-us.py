# -*- coding: utf-8 -*-
"""
Created on Tue Oct 09 20:23:10 2018

python学习爬虫抓取与解析:亚马逊案例
实验目的：批量爬取亚马逊美国asin上线时间
工具：requests和BeautifulSoup

@author: 江异
"""

# 1.准备工作 
# 编写爬虫前的准备工作，我们需要导入用到的库，这里主要使用的是requests和BeautifulSoup两个。还有一个Time库，负责设置每次抓取的休息时间。

import os
# from urllib.request import urlretrieve
import re

import click
import pandas as pd
import pandas as pd
import re
import requests
import requests
import sys
import time
import time
import xlrd
import xlrd
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from fake_useragent import UserAgent
from lxml import etree
from lxml.html import fromstring

start_time = time.time()
# 设置列表页URL的固定部分
url1 = 'https://www.amazon.com/B-Male-GearIT-Meters-Printer-Scanner/product-reviews/'
url2 = '/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=avp_only_reviews&formatType=current_format&pageNumber=1&sortBy=recent'
url3 = '/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&formatType=current_format&pageNumber=1&sortBy=recent'

# 设置请求头部信息
ua = UserAgent()
# headers = {'User-Agent':ua.chrome}
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

proxies = {'proxy': 'http://116.212.157.23:56354'}
# 循环抓取列表页信息
file_path = 'asin-us.xlsx'
workbook = xlrd.open_workbook(file_path)
booksheet = workbook.sheets()[0]
nrows = booksheet.nrows
print('一共' + str(nrows) + '条asin')
results = []

for i in range(nrows):
    etreeee1 = ''
    etreeee2 = ''
    if i == 0:
        pass
    else:
        print('第' + str(i) + '个')
        country = booksheet.row_values(i)[0]
        asin = booksheet.row_values(i)[1].strip()
        fmt_vrp_review, fmt_all_review = '0', '0'

        time.sleep(1.0)
        a1 = url1 + asin + url2
        # r1 = requests.get(url = a1, proxies = proxies)
        r1 = requests.get(url=a1, headers=headers)
        etreeee1 = fromstring(r1.text)
        print('爬取：' + a1)

        if r1.status_code in [304, 503]:
            print('response错误')
            reviews = pd.DataFrame(results)
            reviews.to_excel('reviewscount-us-error.xlsx', index=False)
            sys.exit()
        else:
            pass

        if etreeee1.xpath("*//form[@action='/errors/validateCaptcha']"):
            print('需要验证码')
            reviews = pd.DataFrame(results)
            reviews.to_excel('reviewscount-us-error.xlsx', index=False)
            sys.exit()
        else:
            print('爬取成功')

        html1 = r1.content
        amazonreviews = BeautifulSoup(html1, 'lxml')
        fmt_vrp_reviews = amazonreviews.find_all('div', attrs={'class': 'a-section a-spacing-medium'})
        for c1 in fmt_vrp_reviews:
            try:
                contents1 = c1.span.string
                fmt_vrp_review = contents1.split(' ', 4)[3]

            except:
                print('error')
                continue

        '''
        time.sleep(1.0)
        a2 = (url1 + asin + url3)
        r2 = requests.get(url =a2, headers = headers)
        etreeee2 = fromstring(r1.text)
        print('爬取：' + a2)

        if r2.status_code in [304, 503]:
            print('response错误')
            reviews = pd.DataFrame(results)
            reviews.to_excel('reviewscount-us-error.xlsx', index=False)
            sys.exit()
        else:
            pass

        if etreeee2.xpath("*//form[@action='/errors/validateCaptcha']"):
            print('需要验证码')
            reviews = pd.DataFrame(results)
            reviews.to_excel('reviewscount-us-error.xlsx', index=False)
            sys.exit()
        else:
            print('爬取成功')

        html2 = r2.content
        amazonreviews = BeautifulSoup(html2, 'lxml')
        fmt_all_reviews = amazonreviews.find_all('div', attrs = {'class': 'a-section a-spacing-medium'})
        for c2 in fmt_all_reviews:
            try:
                contents2 = c2.span.string
                fmt_all_review = contents2.split(' ',4)[3]

            except:
                print('error')
                continue
        '''
        print('认证评论：' + str(fmt_vrp_review))
        results.append({
            "country": country,
            "asin": asin,
            "fmt_vrp_review": fmt_vrp_review
        })

reviews = pd.DataFrame(results)
reviews.to_excel('reviewscount-us.xlsx', index=False)

end_time = time.time()
print('共耗时' + str(end_time - start_time) + 's')
