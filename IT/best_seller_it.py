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
url = 'https://www.amazon.it/s?k=bollitore+elettrico&rh=p_72%3A490208031&dc&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1562726048&rnid=490204031&ref=sr_nr_p_72_4'


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
        url = urljoin('https://www.amazon.it', next_url[0])
    elif html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href'):
        next_url = html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href')
        url = urljoin('https://www.amazon.it', next_url[0])
    else:
        break

asins = pd.DataFrame(results)
asins.to_excel('best_seller_it.xlsx', index=False)

end_time = time.time()
print (end_time - start_time)
