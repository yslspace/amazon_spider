# -*- coding: utf-8 -*-
import pandas as pd
import requests
import sys
import time
import xlrd
from lxml import etree
from typing import Any, Union
from urllib.parse import urljoin

start_time = time.time()

# 设置列表页URL的固定部分
url1 = 'https://www.amazon.de/Kochmesser-Küchenmesser-Chefmesser-Allzweckmesser-Rostfreier/product-reviews/'
url2 = '/ref=cm_cr_getr_d_paging_btm_'
url3 = '?ie=UTF8&reviewerType=avp_only_reviews&pageNumber='
url4 = '&formatType=current_format&sortBy=recent'

# 这里，我们最好在http请求中设置一个头部信息，否则很容易被封ip。头部信息网上有很多现成的，也可以使用httpwatch等工具来查看。

# 设置请求头部信息
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.10) Gecko/20100914 Firefox/3.6.10'
}

# 循环抓取列表页信息
file_path = 'asin-de.xlsx'
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
    for j in range(1, 1000):
        time.sleep(2.0)
        a = (url1 + asin + url2 + str(page) + url3 + str(page) + url4)

        if page % 50 == 0:
            print(str(page))
        else:
            print(str(page), end=' ')

        try:
            r = requests.get(url=a, headers=headers)
        except:
            print('请求页出问题，爬取断开')
            results_this_asin.extend(results_this_page)
            # reviews = pd.DataFrame(results)
            # reviews.to_csv('reviews-uk-error.csv', index=False)
            sys.exit()

        html = etree.HTML(r.text)
        results_this_page = []
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

        # if len(results_this_page) == 0 and page != 501:
        #     print('爬取'+str(asin)+'第'+str(page)+'页出问题，爬取断开')
        #     results_this_asin.extend(results_this_page)
        #     # reviews = pd.DataFrame(results)
        #     # reviews.to_csv('reviews-us-error.csv', index=False)
        #     sys.exit()
        # else: pass

        results_this_asin.extend(results_this_page)

        if html.xpath('.//li[@class="a-last"]'):
            page = page + 1
        else:
            print('done')
            break

    if len(results_this_asin) == 0:
        print(str(asin) + '评论为0，爬取断开')
        # reviews = pd.DataFrame(results)
        # reviews.to_csv('reviews-us-error.csv', index=False)
        sys.exit()
    else:
        print('该asin评论数：' + str(len(results_this_asin)))
        results.extend(results_this_asin)

    reviews = pd.DataFrame(results)
    reviews.to_csv('reviews-de.csv', index=False)
end_time = time.time()
print(end_time - start_time)
