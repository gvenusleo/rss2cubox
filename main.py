import time

import feedparser
import requests

from config import *


def log(start_time):
    """
    读取 & 写入程序运行时间
    :param start_time: 第一次运行时发送的最早的文章日期
    :return: 上次运行时间
    """
    with open('log.txt', 'r+', encoding='utf=8') as log_file:
        log_list = log_file.readlines()
        if len(log_list) == 0:
            last_time = time.strptime('2022-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            last_time = time.strptime(log_list[-1][:-2], start_time)
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_file.write(now_time + '\n')
    return last_time


def feed2cubox(api, feed_url, cubox_tags, cubox_folder, last_time):
    """
    发送文章到 Cubox
    :param api: Cubox API
    :param feed_url: 订阅源地址
    :param cubox_tags：指定标签
    :param cubox_folder: 指定收藏夹
    :param last_time: 上次运行时间
    :return: 是否发送成功
    """
    success = True
    feed = feedparser.parse(feed_url)
    update_time = feed.updated_parsed
    if last_time > update_time:
        success = None
    else:
        for entry in feed.entries:
            if 'published_parsed' in entry:
                entry_time = entry.published_parsed
            elif 'updated_parsed' in entry:
                entry_time = entry.updated_parsed
            else:
                entry_time = entry.created_parsed
            if entry_time < last_time:
                break
            article_url = entry.link
            article_title = entry.title
            article_description = entry.description
            data = {
                'type': 'url',
                'content': article_url,
                'title': article_title,
                'description': article_description,
                'tags': cubox_tags,
                'folder': cubox_folder
            }
            r = requests.post(api, json=data)
            if r.json()['code'] != 200 or r.json()['message'] != '':
                success = False
                break
            print(article_title + ' ' + article_url)
    return success


def rss2cubox():
    """
    主程序
    :return: None
    """
    cubox_api = CUBOX_API       # Cubox API
    cubox_tags = CUBOX_TAGS     # 指定文章标签
    cubox_folder = CUBOX_FOLDER # 指定收藏夹
    feed_list = FEED_LIST       # 订阅源地址列表
    start_time = START_TIME     # 第一次运行时发送的最早的文章日期

    print('-' * 30)
    last_time = log(start_time)
    for feed_url in feed_list:
        success = feed2cubox(cubox_api, feed_url, cubox_tags, cubox_folder, last_time)
        if success != False:
            continue
        else:
            print("ERROR!!!!!!!!")
            break
    print('-' * 30)


if __name__ == '__main__':
    rss2cubox()
