# -*- coding: utf-8 -*-
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from functools import wraps
from bs4 import BeautifulSoup

import pymysql
import requests
from lxml import etree
from fake_useragent import UserAgent

from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_CHARSET

UA = UserAgent(path='E:/guanchazhe_spider-master/fakeuseragent.json')

lock = Lock()

mysql_conn = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    charset=MYSQL_CHARSET
)
cursor = mysql_conn.cursor()


def logging(f):
    """ 打印日志的装饰器 """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print('执行{0}失败，错误：{1}'.format(f.__name__, str(e)))
            return None

    return wrapper


def request(url, **kwargs):
    """ 简单封装一下GET请求 """

    kwargs.setdefault('headers', {})
    kwargs['headers'].setdefault('User-Agent', UA.random)
    r = requests.get(url, **kwargs)
    r.encoding = r.apparent_encoding
    return r


@logging
def save(**kwargs):
    """ 保存数据 """

    # 多线程中执行要加锁
    # with lock:

    sql = "insert into hotrows (`data`, `data_type`, `name`) values (%s, %s, %s)"
    cursor.execute(sql, (kwargs.get('data'), kwargs.get('data_type'), kwargs.get('name')))
    mysql_conn.commit()


@logging
def get_fenghuangwang():
    """凤凰网"""
    data_type = 'fenghuang'
    name = '凤凰网'
    url = 'https://www.ifeng.com/'
    html = etree.HTML(request(url).text)
    hot_list = html.xpath('//p[@class="index_news_list_p_5zOEF "]/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text.strip(),
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_ithome():
    """ IT之家"""

    data_type = 'ithome'
    name = 'IT之家'
    url = 'https://www.ithome.com/'

    r = request(url)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//div[@id="rank"]/ul[2]/li/a')
    #

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.xpath('string()'),
            'url': hot.get('href')
        })

    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


# def get_zhihu():
#     """ 爬取知乎热榜 """
#
#     name = '知乎'
#     data_type = 'zhihu'
#     url = 'https://www.zhihu.com/hot'
#
#     response = requests.get(url)
#     html_content = response.text
#
#     soup = BeautifulSoup(html_content, 'html.parser')
#     hot_list = soup.find_all('div', class_='HotItem-content')
#
#     all_data = []
#     for hot in hot_list:
#         a_tag = hot.find('a', class_='HotItem-title')
#         all_data.append({
#             'title': a_tag.text,
#             'url': 'https://www.zhihu.com' + a_tag['href']
#         })
#
#     return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}
#     result = get_zhihu_hotlist()
#     print(result)


# def get_ccut():
#     """ CCUT综合新闻 """
#
#     name = 'CCUT'
#     data_type = 'CCUT'
#     url = 'https://www.ccut.edu.cn/'
#
#     response = requests.get(url)
#     response.encoding='utf-8'
#     html_content = response.text
#
#     soup = BeautifulSoup(html_content, 'html.parser')
#     div_tags = soup.find_all('li')
#
#     all_data = []
#     for hot2 in div_tags:
#         a_text = hot2.find('a').text
#         all_data.append({
#             'title': str(a_text),
#             'url': str(hot2.find('a').get('href'))
#         })
#     return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


# @logging
# def get_weibo():
#     """ 爬取微博热榜 """
#
#     name = '微博'
#     data_type = 'weibo'
#     url = 'https://s.weibo.com/top/summary'
#     response = requests.get(url)
#     html_content = response.text
#     soup = BeautifulSoup(html_content, 'html.parser')
#     hot_list = soup.find_all('td', class_='td-02')
#     all_data = []
#     for hot in hot_list:
#         a_tag = hot.find('a')
#         all_data.append({
#             'title': a_tag.text,
#             'url': 'https://s.weibo.com' + a_tag['href']
#         })
#     return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}
#     # result = get_weibo_hotlist()
#     # print(result)


@logging
def get_tieba():
    """ 百度贴吧 """

    name = '贴吧'
    data_type = 'tieba'
    url = 'http://tieba.baidu.com/hottopic/browse/topicList'

    json_data = request(url).json()
    hot_list = json_data.get('data').get('bang_topic').get('topic_list')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot['topic_name'],
            'url': hot['topic_url']
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_douban():
    """ 豆瓣小组-讨论精选 """

    name = '豆瓣'
    data_type = 'douban'
    url = 'https://www.douban.com/group/explore'
    r = request(url)
    r.encoding = 'utf-8'
    html = etree.HTML(r.text)
    hot_list = html.xpath('//div[@class="bd"]/h3/a')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text,
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data), 'data_type': data_type, 'name': name}


@logging
def get_wangyi():
    """ 网易排行 """

    name = '网易'
    data_type = 'wangyi'
    url = 'https://news.163.com/'
    html = etree.HTML(request(url).text)
    hot_list = html.xpath('//li[@class=" top "]/a')
    # //*[@id="index2016_wrap"]/div[3]/div[2]/div[3]/div[3]/div[10]/ul/li[1]/a

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text.strip(),
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_hupu():
    """ 虎扑步行街热帖 """

    name = '虎扑'
    data_type = 'hupu'
    url = 'https://bbs.hupu.com/all-gambia'

    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    div_tags = soup.find_all('div', class_='t-info')

    all_data = []
    for hot2 in div_tags:
        span_text = hot2.find('span').text
        all_data.append({
            'title': str(span_text),
            'url': 'https://bbs.hupu.com' + str(hot2.find('a').get('href'))
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_github():
    """ GitHub, 网络问题可能会超时, 建议科(fang-)学(-zhi)上(he-)网(-xie) """

    name = 'GitHub'
    data_type = 'github'
    url = 'https://github.com/trending'

    r = request(url)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//h1[@class="h3 lh-condensed"]/a')

    all_data = []
    for hot in hot_list:
        span = hot.xpath('span')[0]
        all_data.append({
            'title': span.text.strip() + span.tail.strip(),
            'url': 'https://github.com' + hot.get('href'),
            'desc': hot.xpath('string(../../p)').strip()
        })
    return {'data': json.dumps(all_data), 'data_type': data_type, 'name': name}


@logging
def get_baidu():
    """ 百度风云榜 """

    name = '百度'
    data_type = 'baidu'
    url = 'http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b1'

    r = request(url)
    html = etree.HTML(r.text)
    hot_list = html.xpath('//div[@class="content_1YWBm"]/a')  # 链接
    hot_list2 = html.xpath('//div[@class="content_1YWBm"]/a/div[1]')  # 标题
    all_data = []
    # for hot2 in hot_list:
    #     for hot in hot_list2:
    #         all_data.append({
    #             'title': str(hot2.text.strip()),
    #             'url': str(hot.get('href'))
    #         })
    #         break;

    for hot, hot2 in zip(hot_list, hot_list2):
        all_data.append({
            'title': str(hot2.text.strip()),
            'url': str(hot.get('href'))
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


@logging
def get_():
    """ template """

    name = ''
    data_type = ''
    url = ''

    html = etree.HTML(request(url).text)
    hot_list = html.xpath('')

    all_data = []
    for hot in hot_list:
        all_data.append({
            'title': hot.text,
            'url': hot.get('href')
        })
    return {'data': json.dumps(all_data, ensure_ascii=False), 'data_type': data_type, 'name': name}


def main():
    try:
        all_func = [
            get_fenghuangwang, get_ithome, get_tieba, get_douban,
            get_wangyi, get_hupu, get_github, get_baidu
        ]

        # 线程池
        with ThreadPoolExecutor(min(len(all_func), 10)) as executor:
            # 线程池执行任务
            all_task = [executor.submit(func) for func in all_func]

            # 同步保存结果
            for future in as_completed(all_task):
                result = future.result()
                if result:
                    print(result)
                    save(**result)
    except:
        import traceback
        traceback.print_exc()

    finally:
        cursor.close()
        mysql_conn.close()


if __name__ == '__main__':
    # 定时执行
    main()
    # print(get_douban())
