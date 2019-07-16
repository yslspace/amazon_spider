# -*- coding: utf-8 -*-
import pandas as pd
import requests
import time
from lxml import etree
from typing import Any, Union
from urllib.parse import urljoin

start_time = time.time()

head = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/11.04 Chromium/18.0.1025.151 Chrome/18.0.1025.151 Safari/535.19'
}

url = 'https://www.amazon.co.jp/%E9%9B%BB%E6%B0%97%E3%82%B1%E3%83%88%E3%83%AB-%E9%9B%BB%E6%B0%97%E3%82%B1%E3%83%88%E3%83%AB%E3%83%BB%E3%82%B8%E3%83%A3%E3%83%BC%E3%83%9D%E3%83%83%E3%83%88-%E3%82%AD%E3%83%83%E3%83%81%E3%83%B3%E5%AE%B6%E9%9B%BB-%E5%AE%B6%E9%9B%BB/b/ref=dp_bc_aui_C_4?ie=UTF8&node=16245081'

results = []
for i in range(1, 100):
    time.sleep(1.0)
    print(url)
    r = requests.get(url, headers=head)
    html = etree.HTML(r.text)
    for element in html.xpath('//div[@class="s-item-container"]'):
        name1 = "".join(
            element.xpath('.//div[@class="a-row a-spacing-mini"]/div[@class="a-row a-spacing-none"]/a/h2/text()'))
        name2 = "".join(element.xpath(
            './/div[@class="a-row a-spacing-mini"]/div[@class="a-row a-spacing-none sx-line-clamp-4"]/a/h2/text()'))
        name = name1 + name2
        asin = "".join(element.xpath('./../@data-asin'))
        reviews = "".join(element.xpath('.//div[@class="a-row a-spacing-none"]/a/text()'))
        results.append({
            "asin": asin,
            "names": name,
            "reviews": reviews
        })

    for element in html.xpath('//div[@data-asin]'):
        name1 = "".join(element.xpath(
            './/div[@class="a-section a-spacing-none"]//a[@class="a-link-normal a-text-normal"]/span/text()'))
        name2 = "".join(element.xpath(
            './/div/div[@class="a-row a-spacing-mini"]/div[@class="a-row a-spacing-none sx-line-clamp-4"]/a/h2/text()'))
        name = name1 + name2
        reviews = "".join(element.xpath('.//a[@class="a-link-normal"]/span/text()'))
        asin = "".join(element.xpath('./@data-asin'))
        results.append({
            "asin": asin,
            "names": name,
            "reviews": reviews
        })
    if html.xpath('.//*[@id="pagnNextLink"]'):
        next_url = html.xpath('.//*[@id="pagnNextLink"]/@href')
        url = urljoin('https://www.amazon.co.jp', next_url[0])
    elif html.xpath('.//li[@class="a-last"]'):
        next_url = html.xpath('.//li[@class="a-last"]/a/@href')
        url = urljoin('https://www.amazon.co.jp', next_url[0])
    else:
        break
asins = pd.DataFrame(results)
asins.to_excel('best_seller_jp.xlsx', index=False)

end_time = time.time()
print (end_time - start_time)
