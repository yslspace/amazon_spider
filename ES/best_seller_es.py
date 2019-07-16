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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
}
url = 'https://www.amazon.es/s?i=kitchen&bbn=2165390031&rh=n%3A2165390031%2Cp_72%3A831283031&dc&pf_rd_i=2165390031&pf_rd_m=A1AT7YVPFBWXBL&pf_rd_p=51b40d23-6371-5683-b0b5-d0dd1900f3f8&pf_rd_p=51b40d23-6371-5683-b0b5-d0dd1900f3f8&pf_rd_r=7TKN28BVNWTPNGQTWM6W&pf_rd_r=7TKN28BVNWTPNGQTWM6W&pf_rd_s=merchandised-search-6&pf_rd_t=101&qid=1562663083&rnid=831271031&ref=sr_nr_p_72_4'


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
        url = urljoin('https://www.amazon.es', next_url[0])
    elif html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href'):
        next_url = html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href')
        url = urljoin('https://www.amazon.es', next_url[0])
    else:
        break

asins = pd.DataFrame(results)
asins.to_excel('best_seller_es.xlsx', index=False)

end_time = time.time()
print (end_time - start_time)
