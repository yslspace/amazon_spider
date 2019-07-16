# -*- coding: utf-8 -*-
from random import choice

import pandas as pd
import requests
import sys
import time
import xlrd
from lxml import etree
from lxml.html import fromstring
from typing import Any, Union
from urllib.parse import urljoin

start_time = time.time()

# 设置列表页URL的固定部分
url1 = 'https://www.amazon.com/Sharp-Pebble-Whetstone-Sharpening-Waterstone/product-reviews/'
url2 = '/ref=cm_cr_getr_d_paging_btm_'
url3 = '?ie=UTF8&reviewerType=avp_only_reviews&pageNumber='
url4 = '&formatType=current_format&sortBy=recent'

# 这里，我们最好在http请求中设置一个头部信息，否则很容易被封ip。头部信息网上有很多现成的，也可以使用httpwatch等工具来查看。

# 设置请求头部信息
headers1 = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50'}
headers3 = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'}

headerslist = ['Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
               'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36']

# 循环抓取列表页信息
file_path = 'asin-us.xlsx'
workbook = xlrd.open_workbook(file_path)
booksheet = workbook.sheets()[1]
nrows = booksheet.nrows
print('一共' + str(nrows - 1) + '条asin')
results = []

for i in range(1, nrows):
    country = booksheet.row_values(i)[0]
    asin = booksheet.row_values(i)[1]
    page = 1
    print('爬取：' + str(asin))
    print('爬取页面首页：' + str(url1 + asin + url2 + str(page) + url3 + str(page) + url4))
    results_this_asin = []
    headers = {'user-agent': choice(headerslist)}
    for j in range(1, 1000):
        time.sleep(2.0)
        a = (url1 + asin + url2 + str(page) + url3 + str(page) + url4)

        if page % 50 == 0:
            print(str(page))
        else:
            print(str(page), end=' ')

        r = requests.get(url=a, headers=headers1)
        html = etree.HTML(r.text)
        etreeee = fromstring(r.text)
        results_this_page = []
        if r.status_code == 300 or r.status_code == 200:
            pass
        else:
            print('response错误')
            sys.exit()
        if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
            print('需要验证码')
            sys.exit()

        for element in html.xpath('.//div[@data-hook="review"]'):
            helpful0 = "".join(element.xpath(
                './/div[5]/div/span[@data-hook="review-voting-widget"]/div[@class="a-row a-spacing-small"]/span/text()'))
            helpful = helpful0.split(' ', 3)[0]
            if helpful == "One":
                helpful = 1
            elif helpful == "":
                helpful = 0

            title = "".join(element.xpath('.//a[@data-hook="review-title"]/span/text()'))
            if title == "":
                title = "".join(element.xpath('.//a[@data-hook="review-title"]/text()'))

            content = "".join(element.xpath('.//div[@class="a-row a-spacing-small review-data"]/span/span/text()'))
            if content == "":
                content = "".join(element.xpath('.//div[@class="a-row a-spacing-small review-data"]/span/text()'))

            results_this_page.append({
                "country": country,
                "asin": asin,
                "rating": "".join(
                    element.xpath('.//div/div[@class="a-row"]/a[@class="a-link-normal"]/i/span/text()')[0][:3]),
                "title": title,
                "date": "".join(element.xpath('.//span[@data-hook="review-date"]/text()')),
                "content": content,
                "colour": "".join(
                    element.xpath('.//div[@class="a-row a-spacing-mini review-data review-format-strip"]/a/text()')),
                "helpful": helpful
            })
        '''
        if len(results_this_page) == 0 and page != 501:
            print('爬取'+str(asin)+'第'+str(page)+'页出问题，爬取断开')
            results_this_asin.extend(results_this_page)
            reviews = pd.DataFrame(results)
            reviews.to_csv('reviews-us-error.csv', index=False)
            sys.exit()
        else: pass
        '''

        results_this_asin.extend(results_this_page)

        if html.xpath('.//li[@class="a-last"]'):
            page = page + 1
        else:
            print('done')
            break

    if len(results_this_asin) == 0:
        print(str(asin) + '评论为0')
    else:
        print('该asin评论数：' + str(len(results_this_asin)))
        results.extend(results_this_asin)
    reviews = pd.DataFrame(results)
    reviews.to_csv('reviews-us.csv', index=False)
end_time = time.time()
print(end_time - start_time)
