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
url1 = 'https://www.amazon.co.uk/Smiths-Edgesport-50264-Adjustable-Sharpener/product-reviews/'
url2 = '/ref=cm_cr_getr_d_paging_btm_prev_'
url3 = '?ie=UTF8&reviewerType=avp_only_reviews&pageNumber='
url4 = '&formatType=current_format&sortBy=recent'

# 这里，我们最好在http请求中设置一个头部信息，否则很容易被封ip。头部信息网上有很多现成的，也可以使用httpwatch等工具来查看。

# 设置请求头部信息
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
}
proxies = {'http': '200.81.169.242:54529'}
# 循环抓取列表页信息
file_path = 'asin-uk.xlsx'
workbook = xlrd.open_workbook(file_path)
booksheet = workbook.sheets()[1]
nrows = booksheet.nrows
print('一共' + str(nrows - 1) + '条asin')
results = []
lastpage = 501

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
        except requests.exceptions.ConnectionError:
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

        if len(results_this_page) == 0 and page != 501 and page != 1:
            print('爬取' + str(asin) + '第' + str(page) + '页出问题，爬取断开')
            results_this_asin.extend(results_this_page)
            # reviews = pd.DataFrame(results)
            # reviews.to_csv('reviews-uk-error.csv', index=False)
            sys.exit()
        else:
            pass

        results_this_asin.extend(results_this_page)

        if html.xpath('.//li[@class="a-last"]'):
            page = page + 1
            # 测试某些ASIN特殊情况
            '''
            if page > lastpage :
                print('爬取到重定向页面，断开爬取')
                results_this_asin.extend(results_this_page)
                reviews = pd.DataFrame(results)
                reviews.to_csv('reviews-uk-error.csv', index=False)
                sys.exit()
                break
            '''
        else:
            print('done')
            lastpage = page
            print('lastpage=' + str(lastpage))
            break

    if len(results_this_asin) == 0:
        print(str(asin) + '评论为0，爬取页面有问题')
        '''
        reviews = pd.DataFrame(results)
        reviews.to_csv('reviews-uk-error.csv', index=False)
        sys.exit()
        '''
    else:
        print('该asin评论数：' + str(len(results_this_asin)))
        results.extend(results_this_asin)
    reviews = pd.DataFrame(results)
    reviews.to_csv('reviews-uk.csv', index=False)
end_time = time.time()
print(end_time - start_time)
