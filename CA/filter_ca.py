# -*- coding: utf-8 -*-
import json
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
from lxml import etree
from lxml.html import fromstring

start_time = time.time()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
proxies = {'proxy': 'http://116.212.157.23:56354'}
url0 = 'https://www.amazon.ca/dp/'
url1 = 'https://www.amazon.ca/KINDEN-Borosilicate-Electric-Electronic-Teakettle/product-reviews/'
url2 = '/ref=cm_cr_arp_d_viewopt_fmt?ie=UTF8&reviewerType=avp_only_reviews&pageNumber=1&formatType=current_format'
url3 = '/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&formatType=current_format&pageNumber=1&sortBy=recent'

file_path = 'asin-ca.xlsx'
workbook = xlrd.open_workbook(file_path)
booksheet = workbook.sheets()[0]
asin_df = pd.read_excel(file_path, usecols=[2], names=None)
asin_count = pd.read_excel(file_path, usecols=[1], names=None)
asinall = asin_df.values.tolist()
nrows = len(asin_count)
print('一共' + str(nrows) + '条asin')
result = []
asinall_list = []
for s_li in asinall:
    asinall_list.append(s_li[0])
strip = lambda items, join_str='': join_str.join([i.strip() for i in items])


def get_message(asin, list_switch):
    a0 = url0 + asin
    a1 = url1 + asin + url2
    print('爬取：' + asin, end='  ')
    time.sleep(1.0)
    r0 = requests.get(url=a0, headers=headers)
    html0 = etree.HTML(r0.text)
    soup0 = BeautifulSoup(r0.text, 'lxml')
    time.sleep(1.0)
    r1 = requests.get(url=a1, headers=headers)
    soup1 = BeautifulSoup(r1.text, 'lxml')
    html1 = etree.HTML(r1.text)
    if r0.status_code in [304, 503] or r1.status_code in [304, 503]:
        print('response错误')
        # results = pd.DataFrame(result)
        # results.to_excel('reviewscount-us-error.xlsx', index=False)
        sys.exit()
    else:
        pass

    if html0.xpath("*//form[@action='/errors/validateCaptcha']") or \
            html1.xpath("*//form[@action='/errors/validateCaptcha']"):
        print('需要验证码')
        # results = pd.DataFrame(result)
        # results.to_excel('reviewscount-us-error.xlsx', index=False)
        sys.exit()
    else:
        print('爬取成功')
    item = dict()
    item['asin'] = asin
    item['title'] = strip(html0.xpath(".//*[@id='productTitle']/text()"))
    item['review_count'] = strip(html0.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
    item['img'] = list(json.loads(html0.xpath(".//img[@id='landingImage']/@data-a-dynamic-image")[0]))[0] \
        if html0.xpath(".//img[@id='landingImage']/@data-a-dynamic-image") else ''

    item['Tips'] = "".join(html0.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                   '').replace(
        r'[', '').replace(r']', '').strip().strip(',').strip()
    # Description1
    try:
        soup01 = soup0.find_all(attrs={"id": "aplus3p_feature_div"})
        Description1dirty = str(BeautifulSoup(str(soup01), 'lxml').div.div.div.find_all(name='div')).replace(
            '\n', '')
        Description1dirty2 = re.sub(r'<table.*</table>', '', Description1dirty)
        reg = re.compile('<[^>]*>')
        Description1 = reg.sub('', Description1dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                   '').replace(
            r']', '').strip().strip(',').strip()
    except:
        Description1 = ''

    # Description2
    try:
        soup01 = soup0.find_all(attrs={"id": "descriptionAndDetails"})
        Description2dirty = str(
            BeautifulSoup(str(soup01), 'lxml').find_all(attrs={"id": "productDescription"}))
        Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
        reg = re.compile('<[^>]*>')
        Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                   '').replace(
            r']', '').strip().strip(',').strip()
    except:
        Description2 = ''

    # manufacturer
    try:
        soup01 = soup0.find_all(attrs={"id": "aplus"})
        manufacturer_dirty = str(BeautifulSoup(str(soup01), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                          '')
        manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
        reg = re.compile('<[^>]*>')
        manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                   '').replace(
            r']', '').strip().strip(',').strip()
    except:
        manufacturer = ''
    item['Description'] = Description1 + Description2 + manufacturer

    fmt_vrp_reviews = soup1.find_all('div', attrs={'class': 'a-section a-spacing-medium'})
    fmt_vrp_review = '0'
    for c1 in fmt_vrp_reviews:
        try:
            contents1 = c1.span.string
            fmt_vrp_review = contents1.split(' ', 4)[3]

        except:
            fmt_vrp_review = 'error'
            continue

    result.append({
        "ASIN": item['asin'],
        "name": item['title'],
        "Tips": item['Tips'],
        "img": item['img'],
        "Description": item['Description'],
        "reviews": item['review_count'],
        "fmt_vrp_review": fmt_vrp_review
    })
    results = pd.DataFrame(result)
    results.to_excel('reviewscount-ca.xlsx', index=False)

    if list_switch is True:
        asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r0.text)
        if asin_map:
            asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
            if len(asin_list) > 0 and len(asin_list) < 10:
                print('爬取变体:')
                for asin_i in asin_list:
                    if asin_i not in asinall_list:
                        get_message(asin_i, list_switch=False)
            print('-------------------------')
        else:
            print('-------------------------')


for i in range(nrows + 1):
    if i == 0:
        pass
    else:
        asin = booksheet.row_values(i)[1].strip()
        get_message(asin, list_switch=True)
