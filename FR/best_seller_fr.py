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
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Ubuntu/10.10 Chromium/11.0.681.0 Chrome/11.0.681.0 Safari/534.21'
}
url = 'https://www.amazon.fr/s?i=kitchen&bbn=57902031&rh=n%3A57902031%2Cp_72%3A437876031&dc&pf_rd_i=57902031&pf_rd_m=A1X6FK5RDHNB96&pf_rd_p=0035fff6-6dc3-52f7-821d-9bc860eb24c2&pf_rd_p=0035fff6-6dc3-52f7-821d-9bc860eb24c2&pf_rd_r=E5M651XKGA4NYWRAVE6F&pf_rd_r=E5M651XKGA4NYWRAVE6F&pf_rd_s=merchandised-search-6&pf_rd_t=101&qid=1562659732&rnid=437872031&ref=sr_nr_p_72_4'


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
        url = urljoin('https://www.amazon.fr', next_url[0])
    elif html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href'):
        next_url = html.xpath('.//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href')
        url = urljoin('https://www.amazon.fr', next_url[0])
    else:
        break

asins = pd.DataFrame(results)
asins.to_excel('best_seller_fr.xlsx', index=False)

end_time = time.time()
print (end_time - start_time)
