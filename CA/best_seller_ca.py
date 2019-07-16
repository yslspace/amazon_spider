# -*- coding: utf-8 -*-
import os

import pandas as pd
import requests
import sys
import time
from lxml import etree
from typing import Any, Union
from urllib.parse import urljoin
from urllib.request import urlretrieve

start_time = time.time()
head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19'
}
url = 'https://www.amazon.ca/b/ref=dp_bc_aui_C_5?ie=UTF8&node=6647628011'


def download(asin, img, download_path):
    urlretrieve(img, os.path.join(download_path, '%s.jpg' % (asin)))


results = []
for i in range(1, 100):
    time.sleep(1.0)
    print(url)
    r = requests.get(url, headers=head)
    html = etree.HTML(r.text)
    for element in html.xpath('.//li[@data-asin]'):
        asin = "".join(element.xpath('.//@data-asin'))
        reviews = "".join(
            element.xpath('.//div[@class="s-item-container"]/div[@class="a-row a-spacing-none"]/a/text()'))
        imgurl = "".join(element.xpath('.//a[@class="a-link-normal a-text-normal"]/img/@src'))
        name = "".join(element.xpath('.//h2[@class="a-size-base s-inline s-access-title a-text-normal"]/text()'))
        if imgurl == '':
            imgurl = "".join(element.xpath('.//div[@class="a-section aok-relative s-image-square-aspect"]/img/@src'))

        if imgurl == '':
            imgurl = "".join(element.xpath('.//div[@class="a-section aok-relative s-image-fixed-height"]/img/@src'))

        if imgurl == '':
            imgurl = "".join(element.xpath('.//div[@class="a-section aok-relative s-image-fixed-height"]/img/@src'))

        if reviews == '':
            reviews = "".join(element.xpath(
                './/div[@class="a-column a-span5 a-span-last"]/div[@class="a-row a-spacing-mini"]/a/text()'))
        else:
            continue
        if reviews != '':
            reviewtest = reviews
        else:
            reviewtest = '1'
        '''
        if imgurl != '' and int(reviewtest.replace(',','')) > 30:
            # print(asin, img1)
            pypath = os.getcwd()
            download(asin, imgurl, pypath + '\\pic2')
        else:
            continue
        '''

        results.append({
            "asin": asin,
            "reviews": reviews,
            "imgurl": imgurl,
            "name": name
        })

    for element in html.xpath('.//div[@data-asin]'):
        imgurl = "".join(element.xpath('.//div[@class="a-section aok-relative s-image-fixed-height"]/img/@src'))
        if imgurl == '':
            imgurl = "".join(element.xpath('.//div[@class="a-section aok-relative s-image-square-aspect"]/img/@src'))

        if imgurl == '':
            imgurl = "".join(element.xpath('.//div[@class="a-section aok-relative s-image-fixed-height"]/img/@src'))

        if imgurl == '':
            imgurl = "".join(element.xpath('.//a[@class="a-link-normal a-text-normal"]/img/@src'))
        asin = "".join(element.xpath('.//@data-asin'))
        reviews = "".join(element.xpath('.//a[@class="a-link-normal"]/span[@class="a-size-base"]/text()'))
        if reviews != '':
            reviewtest = reviews
        else:
            reviewtest = '1'
        '''
        if imgurl != '' and int(reviewtest.replace(',','')) > 30:
            # print(asin, img1)
            pypath = os.getcwd()
            download(asin, imgurl, pypath + '\\pic2')
        else:
            continue
        '''

        name = "".join(element.xpath('.//span[@class="a-size-medium a-color-base a-text-normal"]/text()'))
        if name == "":
            name = "".join(element.xpath('.//a[@class="a-link-normal a-text-normal"]/span/text()'))

        results.append({
            "asin": asin,
            "reviews": reviews,
            "imgurl": imgurl,
            "name": name
        })
    if html.xpath('.//*[@id="pagnNextLink"]'):
        next_url = html.xpath('.//*[@id="pagnNextLink"]/@href')
        url = urljoin('https://www.amazon.ca', next_url[0])
    elif html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href'):
        next_url = html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href')
        url = urljoin('https://www.amazon.ca', next_url[0])
    else:
        break
    asins = pd.DataFrame(results)
    asins.to_excel('best_seller_ca.xlsx', index=False)

end_time = time.time()
print (end_time - start_time)
