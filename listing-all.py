import os
import re
import sys
import time

import click
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml import etree
from lxml.html import fromstring
from urllib.request import urlretrieve

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.8 (KHTML, like Gecko) Version/8.0.3 Safari/600.4.8'}
proxies = {'http': 'http://39.134.67.210:8080'}

get_float = lambda x: float(re.findall('[\d,\.]+', x)[0]) if re.findall('[\d,\.]+', x) else 9999999999
get_category_id = lambda url: re.findall('(bestsellers|zgbs)/(.+?)(/ref|\?){1}', url + '?')[0][1] if re.findall(
    '(bestsellers|zgbs)/(.+?)(/ref|\?){1}', url + '?') else '/'
strip = lambda items, join_str='': join_str.join([i.strip() for i in items])


@click.command()
@click.option('--country', type=str, help='国家的简称，例如US')
@click.option('--asin-file', type=str, help='包含ASIN列表的txt文件')
def crawl(country, asin_file):
    url = ''
    ua = UserAgent()
    if not os.path.exists(asin_file):
        print("文件 %s 不存在！按下回车键结束程序..." % asin_file)
        input()
        sys.exit()
    else:
        pass

    market = country.strip().lower()
    print('爬取站点为：' + str(market))
    if market == 'us':
        listing_us(asin_file)
    elif market == 'uk':
        listing_uk(asin_file)
    elif market == 'de':
        listing_de(asin_file)
    elif market == 'jp':
        listing_jp(asin_file)
    elif market == 'es':
        listing_es(asin_file)
    elif market == 'fr':
        listing_fr(asin_file)
    elif market == 'it':
        listing_it(asin_file)
    elif market == 'ca':
        listing_ca(asin_file)
    else:
        print('market not exist')
        sys.exit()


def download(asin, img, download_path):
    urlretrieve(img, os.path.join(download_path, '%s.jpg' % (asin)))
    print('已下载%s的第1张照片' % (asin))


def listing_us(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        nrows = len(open(asin_file, 'r').readlines())
        print('一共 ' + str(nrows) + ' 条ASIN')
        for asin in f.readlines():
            asin = asin.strip()
            time.sleep(1.0)
            url = 'https://www.amazon.com/dp/' + asin
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                print('response错误')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'US'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))
            item['brand_url'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/@href"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            """
            img_list = re.findall('"hiRes":"(.*?)"', r.text)
            try:
                item['img1'] = img_list[0]
                item['img2'] = img_list[1]
                item['img3'] = img_list[2]
                item['img4'] = img_list[3]
                item['img5'] = img_list[4]
            except:
                pass
            """
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'sold by Amazon' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'
            item['seller_id'] = \
                ''.join(re.findall('seller=(.+?)&', etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href")[0] + '&')) \
                    if etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href") else ''

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # Tips
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            # Description1
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0
            '''
            #爬取图片
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                #print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic2')
            '''

            # 解析 上架时间和排名
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Date")).parent if tmp.find(
                    string=re.compile("Date")) else None
                asin_soup = tmp.find(string=re.compile("ASIN")).parent if tmp.find(string=re.compile("ASIN")) else None
            else:
                issue_date_soup = None
                asin_soup = None

            if issue_date_soup:
                item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
            else:
                item['issue_date'] = None

            if asin_soup:
                item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

            if soup.find(attrs={'id': 'SalesRank'}):
                item['bsr1'] = soup.find(attrs={'id': 'SalesRank'}).get_text()
                item['bsr1path'] = get_category_id(soup.find(attrs={'id': 'SalesRank'}).find('a').attrs['href'])

                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()
                        item['bsr%ipath' % (index + 2)] = '>'.join(
                            [get_category_id(a.attrs['href']) for a in
                             element.find(attrs={'class': "zg_hrsr_ladder"}).find_all('a')])

            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('issue_date', None) is None:
                    issue_date_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Date")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Date")) else None
                    if issue_date_soup:
                        item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
                    else:
                        item['issue_date'] = ''

                if item.get('asin2', None) is None:
                    asin_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")) else None
                    if asin_soup:
                        item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

                if item.get('bsr1', None) is None:
                    rank_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Rank")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Rank")) else None
                    if rank_soup:
                        for index, element in enumerate(rank_soup.parent.find('span').find_all('span')):
                            item['bsr%i' % (index + 1)] = element.get_text('')
                            item['bsr%ipath' % (index + 1)] = '>'.join(
                                [get_category_id(a.attrs['href']) for a in element.find_all('a')])
            if item.get('bsr1', None) is None:
                item['bsr1'] = ''
            if item.get('bsr1path', None) is None:
                item['bsr1path'] = ''
            if item.get('issue_date', None) is None:
                item['issue_date'] = ''
            if item.get('asin2', None) is None:
                item['asin2'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']

            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'].replace('\n', ''),
                "category": item['bsr1path'],
                "上线时间": item['issue_date'],
                "realasin": item['asin2']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_us.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


def listing_uk(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        for asin in f.readlines():
            asin = asin.strip()
            time.sleep(1.0)
            url = 'https://www.amazon.co.uk/dp/' + asin
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                print('response错误')
                sys.exit()
            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'UK'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))
            item['brand_url'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/@href"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'Dispatched from and sold by' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'
            item['seller_id'] = \
                ''.join(re.findall('seller=(.+?)&', etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href")[0] + '&')) \
                    if etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href") else ''

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # 爬取产品介绍
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0

            # 爬取图片
            '''
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                # print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic')
            '''

            # 解析 上架时间和排名 asin
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Date")).parent \
                    if tmp.find(string=re.compile("Date")) else None
            else:
                issue_date_soup = None

            if issue_date_soup:
                item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])

            if soup.find(attrs={'id': 'SalesRank'}):
                item['bsr1'] = ''.join(
                    re.findall('\d+',
                               ''.join(html.xpath('(//*[@id="SalesRank"]//span[@class="zg_hrsr_rank"])[1]/text()'))))
                if item['bsr1']:
                    item['bsr1path'] = get_category_id(soup.find(attrs={'id': 'SalesRank'}).find('a').attrs['href'])

                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()

            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('issue_date', None) is None:
                    issue_date_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Date")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Date")) else None
                    if issue_date_soup:
                        item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])

                if item.get('bsr1', None) is None:
                    for i, j in enumerate(html.xpath(
                            '//*[@id="prodDetails"]/div//ul[@class="zg_hrsr"]/preceding-sibling::node()')):
                        if ' (' in j:  # 符号要修改
                            item['bsr1'] = ''.join(re.findall('\d+', j.strip()))
                            item['bsr1path'] = ''.join(html.xpath(
                                '//*[@id="prodDetails"]/div//ul[@class="zg_hrsr"]/preceding-sibling::node()')[
                                                           i].strip())
                            break
                    for index, element in enumerate(
                            html.xpath('''//*[@id="prodDetails"]/div/div//ul/li[@class="zg_hrsr_item"]''')):
                        item['bsr%i' % (index + 2)] = ''.join(
                            element.xpath('span[@class="zg_hrsr_rank"]/text()'))
                        item['bsr%ipath' % (index + 2)] = ''.join(
                            ''.join(element.xpath('span[@class="zg_hrsr_ladder"]/a/@href')))
            if item.get('bsr1', None) is None:
                item['bsr1'] = ''
            if item.get('bsr1path', None) is None:
                item['bsr1path'] = ''
            if item.get('issue_date', None) is None:
                item['issue_date'] = ''
            if item.get('asin2', None) is None:
                item['asin2'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']
            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'].replace('\n', ''),
                "category": item['bsr1path'],
                "上线时间": item['issue_date'],
                "asinreal": item['asin2']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_uk.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


def listing_de(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        nrows = len(open(asin_file, 'r').readlines())
        print('一共 ' + str(nrows) + ' 条ASIN')
        for asin in f.readlines():
            asin = asin.strip()
            urllan = '?language=en_US'
            time.sleep(1.0)
            url = 'https://www.amazon.de/dp/' + asin
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                print('response错误')
                sys.exit()
            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'DE'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))
            item['brand_url'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/@href"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'Dispatched from and sold by' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'
            item['seller_id'] = \
                ''.join(re.findall('seller=(.+?)&', etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href")[0] + '&')) \
                    if etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href") else ''

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # 爬取产品介绍
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0
            '''
            # 爬取图片
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                # print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic')
            '''

            # 解析 上架时间和排名
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Date")).parent \
                    if tmp.find(string=re.compile("Date")) else None

            if soup.find(attrs={'id': 'SalesRank'}):
                try:
                    item['bsr1'] = html.xpath('//*[@id="SalesRank"]/text()')[1].replace('\n', '').replace('\r', '')
                    item['bsr1path'] = html.xpath('//*[@id="SalesRank"]/text()')[1]
                except:
                    item['bsr1'] = html.xpath('//*[@id="SalesRank"]/td[2]/text()')[0].replace('\n', '').replace('\r',
                                                                                                                '')
                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()
                        item['bsr%ipath' % (index + 2)] = '>'.join(
                            [get_category_id(a.attrs['href']) for a in
                             element.find(attrs={'class': "zg_hrsr_ladder"}).find_all('a')])

            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('bsr1', None) is None:
                    for i, j in enumerate(html.xpath(
                            '//*[@id="prodDetails"]/div//ul[@class="zg_hrsr"]/preceding-sibling::node()')):
                        if r' (' in j:  # 符号要修改
                            item['bsr1'] = ''.join(j.strip())
                            item['bsr1path'] = ''.join(html.xpath(
                                '//*[@id="prodDetails"]/div//ul[@class="zg_hrsr"]/preceding-sibling::node()')[
                                                           i]).strip()
                            break
                    for index, element in enumerate(
                            html.xpath('''//*[@id="prodDetails"]/div/div//ul/li[@class="zg_hrsr_item"]''')):
                        item['bsr%i' % (index + 2)] = ''.join(
                            element.xpath('span[@class="zg_hrsr_rank"]/text()'))
                        item['bsr%ipath' % (index + 2)] = ''.join(
                            get_category_id(''.join(element.xpath('span[@class="zg_hrsr_ladder"]/a/@href'))))
            if item.get('bsr1', None) is None:
                item['bsr1'] = ''
            if item.get('bsr1path', None) is None:
                item['bsr1path'] = ''
            if item.get('issue_date', None) is None:
                item['issue_date'] = ''
            if item.get('asin2', None) is None:
                item['asin2'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']
            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'],
                "category": ''
                # "上线时间": item['issue_date'],
                # "realasin": item['asin2']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_de.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


def listing_jp(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        for asin in f.readlines():
            asin = asin.strip()
            urllan = '?language=en_US'
            time.sleep(1.0)
            url = 'https://www.amazon.co.jp/dp/' + asin + urllan
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                print(r.status_code)
                print(url)
                print('response错误')
                sys.exit()

            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'ES'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'Dispatched from and sold by' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # 爬取产品介绍
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0

            # 爬取图片
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                # print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic')

            # 解析 上架时间和排名
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Amazon\.co\.jp")).parent \
                    if tmp.find(string=re.compile("Amazon\.co\.jp")) else None
            else:
                issue_date_soup = None

            if issue_date_soup:
                item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
            else:
                item['issue_date'] = None

            if soup.find(attrs={'id': 'SalesRank'}):
                item['bsr1'] = soup.find(attrs={'id': 'SalesRank'}).get_text()
                item['bsr1path'] = get_category_id(soup.find(attrs={'id': 'SalesRank'}).find('a').attrs['href'])

                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()
                        item['bsr%ipath' % (index + 2)] = '>'.join(
                            [get_category_id(a.attrs['href']) for a in
                             element.find(attrs={'class': "zg_hrsr_ladder"}).find_all('a')])

            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('issue_date', None) is None:
                    issue_date_soup = soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Date")).parent if soup.find(
                        attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Date")) else None
                    if issue_date_soup:
                        item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
                    else:
                        item['issue_date'] = ''

                if item.get('bsr1', None) is None:
                    rank_soup = soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Bestseller")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Bestseller")) else None
                    if rank_soup:
                        for index, element in enumerate(rank_soup.parent.find('span').find_all('span')):
                            item['bsr%i' % (index + 1)] = element.get_text('')
                            item['bsr%ipath' % (index + 1)] = '>'.join(
                                [get_category_id(a.attrs['href']) for a in element.find_all('a')])
                    else:
                        item['bsr1'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']
            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'].replace('\n', ''),
                "category": item['bsr1path'],
                "上线时间": item['issue_date']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_jp.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


def listing_es(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        for asin in f.readlines():
            asin = asin.strip()
            urllan = '?language=en_GB'
            time.sleep(1.0)
            url = 'https://www.amazon.es/dp/' + asin
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                print('response错误')
                sys.exit()
            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'ES'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'Dispatched from and sold by' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # 爬取产品介绍
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0

            # 爬取图片
            '''
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                # print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic')
            '''

            # 解析 上架时间和排名
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Amazon\.es desde")).parent if tmp.find(
                    string=re.compile("Amazon\.es desde")) else None
                asin_soup = tmp.find(string=re.compile("ASIN")).parent if tmp.find(string=re.compile("ASIN")) else None
            else:
                issue_date_soup = None
                asin_soup = None

            if issue_date_soup:
                item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
            else:
                item['issue_date'] = None

            if asin_soup:
                item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

            if soup.find(attrs={'id': 'SalesRank'}):
                item['bsr1'] = soup.find(attrs={'id': 'SalesRank'}).get_text()
                item['bsr1path'] = get_category_id(soup.find(attrs={'id': 'SalesRank'}).find('a').attrs['href'])

                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()
                        item['bsr%ipath' % (index + 2)] = '>'.join(
                            [get_category_id(a.attrs['href']) for a in
                             element.find(attrs={'class': "zg_hrsr_ladder"}).find_all('a')])

            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('issue_date', None) is None:
                    issue_date_soup = soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Amazon\.es desde")).parent if soup.find(
                        attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Amazon\.es desde")) else None
                    if issue_date_soup:
                        item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
                    else:
                        item['issue_date'] = ''

                if item.get('asin2', None) is None:
                    asin_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")) else None
                    if asin_soup:
                        item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

                if item.get('bsr1', None) is None:
                    rank_soup = soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Clasificaci")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Clasificaci")) else None
                    if rank_soup:
                        for index, element in enumerate(rank_soup.parent.find('span').find_all('span')):
                            item['bsr%i' % (index + 1)] = element.get_text('')
                            item['bsr%ipath' % (index + 1)] = '>'.join(
                                [get_category_id(a.attrs['href']) for a in element.find_all('a')])
                    else:
                        item['bsr1'] = ''
            if item.get('bsr1', None) is None:
                item['bsr1'] = ''
            if item.get('bsr1path', None) is None:
                item['bsr1path'] = ''
            if item.get('issue_date', None) is None:
                item['issue_date'] = ''
            if item.get('asin2', None) is None:
                item['asin2'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']
            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'].replace('\n', ''),
                "category": item['bsr1'],
                "上线时间": item['issue_date'],
                "realasin": item['asin2']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_es.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


def listing_fr(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        for asin in f.readlines():
            asin = asin.strip()
            urllan = '?language=en_GB'
            time.sleep(1.0)
            url = 'https://www.amazon.fr/dp/' + asin + urllan
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                print('response错误')
                sys.exit()
            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'FR'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'Dispatched from and sold by' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # 爬取产品介绍
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0

            # 爬取图片
            '''
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                # print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic')
            '''
            # 解析 上架时间和排名
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Date")).parent if tmp.find(
                    string=re.compile("Date")) else None
                asin_soup = tmp.find(string=re.compile("ASIN")).parent if tmp.find(string=re.compile("ASIN")) else None
            else:
                issue_date_soup = None
                asin_soup = None

            if issue_date_soup:
                item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])

            if asin_soup:
                item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

            if soup.find(attrs={'id': 'SalesRank'}):
                item['bsr1'] = soup.find(attrs={'id': 'SalesRank'}).get_text()
                item['bsr1path'] = get_category_id(soup.find(attrs={'id': 'SalesRank'}).find('a').attrs['href'])

                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()
                        item['bsr%ipath' % (index + 2)] = '>'.join(
                            [get_category_id(a.attrs['href']) for a in
                             element.find(attrs={'class': "zg_hrsr_ladder"}).find_all('a')])
            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('issue_date', None) is None:
                    issue_date_soup = soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("Date")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Date")) else None
                    if issue_date_soup:
                        item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
                    else:
                        item['issue_date'] = ''

                if item.get('asin2', None) is None:
                    asin_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")) else None
                    if asin_soup:
                        item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

                if item.get('bsr1', None) is None:
                    rank_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("vendidos")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("vendidos")) else None
                    if rank_soup:
                        for index, element in enumerate(rank_soup.parent.find('td').find_all(attrs={'class': 'value'})):
                            item['bsr%i' % (index + 1)] = element.get_text('')
                            item['bsr%ipath' % (index + 1)] = '>'.join(
                                [get_category_id(a.attrs['href']) for a in element.find_all('a')])

            if item.get('bsr1', None) is None:
                item['bsr1'] = ''
            if item.get('bsr1path', None) is None:
                item['bsr1path'] = ''
            if item.get('issue_date', None) is None:
                item['issue_date'] = ''
            if item.get('asin2', None) is None:
                item['asin2'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']
            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'].replace('\n', ''),
                "category": item['bsr1path'],
                "上线时间": item['issue_date'],
                "realasin": item['asin2']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_fr.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


def listing_it(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        for asin in f.readlines():
            asin = asin.strip()
            urllan = '?language=en_GB'
            time.sleep(1.0)
            url = 'https://www.amazon.it/dp/' + asin + urllan
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                print('response错误')
                sys.exit()
            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'ES'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'Dispatched from and sold by' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # 爬取产品介绍
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0

            # 爬取图片
            '''
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                # print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic')
            '''
            # 解析 上架时间和排名
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Disponibile")).parent if tmp.find(
                    string=re.compile("Disponibile")) else None
                asin_soup = tmp.find(string=re.compile("ASIN")).parent if tmp.find(string=re.compile("ASIN")) else None
            else:
                issue_date_soup = None
                asin_soup = None

            if issue_date_soup:
                item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])

            if asin_soup:
                item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

            if soup.find(attrs={'id': 'SalesRank'}):
                item['bsr1'] = soup.find(attrs={'id': 'SalesRank'}).get_text()
                item['bsr1path'] = get_category_id(soup.find(attrs={'id': 'SalesRank'}).find('a').attrs['href'])

                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()
                        item['bsr%ipath' % (index + 2)] = '>'.join(
                            [get_category_id(a.attrs['href']) for a in
                             element.find(attrs={'class': "zg_hrsr_ladder"}).find_all('a')])
            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('issue_date', None) is None:
                    issue_date_soup = soup.find(attrs={'id': 'prodDetails'}).find(
                        string=re.compile("mise")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("mise")) else None
                    if issue_date_soup:
                        item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])

                if item.get('asin2', None) is None:
                    asin_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")) else None
                    if asin_soup:
                        item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

                if item.get('bsr1', None) is None:
                    rank_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("partire")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("partire")) else None
                    if rank_soup:
                        for index, element in enumerate(rank_soup.parent.find('td').find_all(attrs={'class': 'value'})):
                            item['bsr%i' % (index + 1)] = element.get_text('')
                            item['bsr%ipath' % (index + 1)] = '>'.join(
                                [get_category_id(a.attrs['href']) for a in element.find_all('a')])
            if item.get('bsr1', None) is None:
                item['bsr1'] = ''
            if item.get('bsr1path', None) is None:
                item['bsr1path'] = ''
            if item.get('issue_date', None) is None:
                item['issue_date'] = ''
            if item.get('asin2', None) is None:
                item['asin2'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']
            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'].replace('\n', ''),
                "category": item['bsr1path'],
                "上线时间": item['issue_date'],
                "realasin": item['asin2']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_it.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


def listing_ca(asin_file):
    start_time = time.time()
    results = []
    with open(asin_file, 'r') as f:
        print('读取txt文件成功')
        nrows = len(open(asin_file, 'r').readlines())
        print('一共 ' + str(nrows) + ' 条ASIN')
        for asin in f.readlines():
            asin = asin.strip()
            time.sleep(1.0)
            url = 'https://www.amazon.ca/dp/' + asin
            r = requests.get(url, headers=headers)
            html_text = r.text
            html = etree.HTML(r.text)
            soup = BeautifulSoup(html_text, 'lxml')
            etreeee = fromstring(r.text)

            # 检查状态码
            if r.status_code == 300 or r.status_code == 200:
                pass
            else:
                print('response错误')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            # 检查页面是否有验证码
            if etreeee.xpath("*//form[@action='/errors/validateCaptcha']"):
                print('需要验证码')
                reviews = pd.DataFrame(results)
                reviews.to_excel('listing.xlsx', index=False)
                sys.exit()
            else:
                print('爬取：' + url)
            item = dict()
            item['country'] = 'CA'
            item['asin'] = asin
            item['title'] = strip(etreeee.xpath(".//*[@id='productTitle']/text()"))
            item['brand'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/text()"))
            item['brand_url'] = strip(etreeee.xpath(".//*[@id='bylineInfo' or @id='brand']/@href"))

            item['review_count'] = strip(etreeee.xpath('.//*[@id="acrCustomerReviewText"]/text()'))
            # item['ask_count'] = strip(etreeee.xpath(".//*[@id='askATFLink']/span/text()"))
            item['rating'] = strip(etreeee.xpath('.//span[@id="acrPopover"]/@title'))
            """
            img_list = re.findall('"hiRes":"(.*?)"', r.text)
            try:
                item['img1'] = img_list[0]
                item['img2'] = img_list[1]
                item['img3'] = img_list[2]
                item['img4'] = img_list[3]
                item['img5'] = img_list[4]
            except:
                pass
            """
            item['soldby'] = strip(etreeee.xpath(".//*[@id='merchant-info']/a[1]/text()"))
            if item['soldby'] == '' and (
                    'sold by Amazon' in ''.join(etreeee.xpath(".//*[@id='merchant-info']/text()"))):
                item['soldby'] = 'Amazon'
            item['seller_id'] = \
                ''.join(re.findall('seller=(.+?)&', etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href")[0] + '&')) \
                    if etreeee.xpath(".//*[@id='merchant-info']/a[1]/@href") else ''

            Description1 = ''
            Description2 = ''
            manufacturer = ''
            Tips = ''
            # Tips
            Tips = "".join(html.xpath('.//*[@id="feature-bullets"]/ul/li/span/text()')).replace('\n', '').replace('\r',
                                                                                                                  '').replace(
                r'[', '').replace(r']', '').strip().strip(',').strip()
            # Description1
            try:
                soup1 = soup.find_all(attrs={"id": "aplus3p_feature_div"})
                Description1dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.div.find_all(name='div')).replace(
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
                soup1 = soup.find_all(attrs={"id": "descriptionAndDetails"})
                Description2dirty = str(
                    BeautifulSoup(str(soup1), 'lxml').find_all(attrs={"id": "productDescription"}))
                Description2dirty2 = re.sub(r'<table.*</table>', '', Description2dirty)
                reg = re.compile('<[^>]*>')
                Description2 = reg.sub('', Description2dirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                Description2 = ''

            # manufacturer
            try:
                soup1 = soup.find_all(attrs={"id": "aplus"})
                manufacturer_dirty = str(BeautifulSoup(str(soup1), 'lxml').div.div.find_all(name='div')).replace('\n',
                                                                                                                 '')
                manufacturerdirty2 = re.sub(r'<table.*</table>', '', manufacturer_dirty)
                reg = re.compile('<[^>]*>')
                manufacturer = reg.sub('', manufacturerdirty2).replace('\n', '').replace('\r', '').replace(r'[',
                                                                                                           '').replace(
                    r']', '').strip().strip(',').strip()
            except:
                manufacturer = ''

            # 解析价格
            buybox_price = strip(etreeee.xpath('//*[@id="price_inside_buybox" or @id="newBuyBoxPrice"]/text()'))
            if buybox_price:
                item['price'] = buybox_price
            else:
                list_price = strip(etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//*[@id='price']/table/tr[not(@id)]/td[2]//text()") else ''
                sale_price = strip(etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_saleprice_row']/td[2]//text()") else ''
                price = strip(etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_ourprice_row']/td[2]//text()") else ''
                deal_price = strip(etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()")[:2]) \
                    if etreeee.xpath(".//tr[@id='priceblock_dealprice_row']/td[2]//text()") else ''
                try:
                    item['price'] = min(
                        [get_float(list_price), get_float(sale_price), get_float(price), get_float(deal_price)])
                except ValueError:
                    item['price'] = 0
                if item['price'] == 9999999999:
                    item['price'] = 0
            '''
            #爬取图片
            rtext = r.text
            img1 = re.findall('data-a-dynamic-image="{&quot;(.*?)&', r.text)
            if img1 == '':
                pass
            else:
                img1 = ''.join(img1[0])
                #print(asin, img1)
                pypath = os.getcwd()
                download(asin, img1, pypath + '\\pic2')
            '''

            # 解析 上架时间和排名
            # 页面一
            tmp = soup.find(attrs={'id': 'detail-bullets'}) or soup.find(attrs={'id': 'detail_bullets_id'})
            if tmp:
                issue_date_soup = tmp.find(string=re.compile("Date")).parent if tmp.find(
                    string=re.compile("Date")) else None
                asin_soup = tmp.find(string=re.compile("ASIN")).parent if tmp.find(string=re.compile("ASIN")) else None
            else:
                issue_date_soup = None
                asin_soup = None

            if issue_date_soup:
                item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
            else:
                item['issue_date'] = None

            if asin_soup:
                item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

            if soup.find(attrs={'id': 'SalesRank'}):
                item['bsr1'] = soup.find(attrs={'id': 'SalesRank'}).get_text()
                item['bsr1path'] = get_category_id(soup.find(attrs={'id': 'SalesRank'}).find('a').attrs['href'])

                rank_soup = soup.find(attrs={'id': 'SalesRank'}).find('ul')
                if rank_soup:
                    for index, element in enumerate(rank_soup.find_all('li', attrs={'class': "zg_hrsr_item"})):
                        item['bsr%i' % (index + 2)] = element.find(attrs={'class': "zg_hrsr_rank"}).get_text()
                        item['bsr%ipath' % (index + 2)] = '>'.join(
                            [get_category_id(a.attrs['href']) for a in
                             element.find(attrs={'class': "zg_hrsr_ladder"}).find_all('a')])

            # 页面二
            if soup.find(attrs={'id': 'prodDetails'}):
                if item.get('issue_date', None) is None:
                    issue_date_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Date")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Date")) else None
                    if issue_date_soup:
                        item['issue_date'] = ''.join([i.string.strip() for i in issue_date_soup.next_siblings])
                    else:
                        item['issue_date'] = ''

                if item.get('asin2', None) is None:
                    asin_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("ASIN")) else None
                    if asin_soup:
                        item['asin2'] = ''.join([i.string.strip() for i in asin_soup.next_siblings])

                if item.get('bsr1', None) is None:
                    rank_soup = soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Rank")).parent \
                        if soup.find(attrs={'id': 'prodDetails'}).find(string=re.compile("Rank")) else None
                    if rank_soup:
                        for index, element in enumerate(rank_soup.parent.find('span').find_all('span')):
                            item['bsr%i' % (index + 1)] = element.get_text('')
                            item['bsr%ipath' % (index + 1)] = '>'.join(
                                [get_category_id(a.attrs['href']) for a in element.find_all('a')])
            if item.get('bsr1', None) is None:
                item['bsr1'] = ''
            if item.get('bsr1path', None) is None:
                item['bsr1path'] = ''
            if item.get('issue_date', None) is None:
                item['issue_date'] = ''
            if item.get('asin2', None) is None:
                item['asin2'] = ''

            asin_map = re.findall('"dimensionToAsinMap" : {(.+)', r.text)
            if asin_map:
                asin_list = re.findall('".*?":"(.*?)"', asin_map[0])
                if asin_list:
                    item['asin_list'] = '|'.join(asin_list)
                else:
                    item['asin_list'] = item['asin']

            results.append({
                "Asins": item['asin'],
                "country": item['country'],
                "Tips": Tips,
                "Description2": Description1,
                "Description1": Description2,
                "manufacturer": manufacturer,
                "name": item['title'],
                "rating": item['rating'],
                "reviews": item['review_count'],
                "price": item['price'],
                "brand": item['brand'],
                "seller": item['soldby'],
                # "asinlist": item['asin_list'],
                "rank": item['bsr1'].replace('\n', ''),
                "category": item['bsr1path'],
                "上线时间": item['issue_date'],
                "realasin": item['asin2']
            })
            reviews = pd.DataFrame(results)
            reviews.to_excel('listing_ca.xlsx', index=False)
    end_time = time.time()
    spend_time = end_time - start_time
    print('一共爬取了' + str(len(results)) + '条asin，耗时' + str(round(spend_time / 60, 1)) + '分钟')


if __name__ == '__main__':
    crawl()
