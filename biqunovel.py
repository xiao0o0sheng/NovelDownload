# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2023/2/26 12:59
# @Author : Xiaosheng Jin
# @Email : xiaosheng7@126.com
# @File : 笔趣阁小说爬取.py
# @Software: PyCharm

import os
import sys
import threading
import time

import parsel
import requests

"""
    此脚本仅针对  https://www.bqg56.com  这个网站
"""


# 按书名检索，找到对应小说的url地址
def novel_url():
    url = 'https://www.bqg56.com/s'
    book_name = input('请输入你想下载的小说名(按q推出)：')
    if book_name in ['q', 'Q']:
        sys.exit()
    params = {'q': str(book_name)}
    response = requests.get(url=url, params=params)
    selector = parsel.Selector(response.text)
    try:
        novels = selector.xpath('//h4/a')
        for n in novels:
            if book_name == n.xpath('./text()').get():
                print('\n已找到 {} 的资源链接\n'.format(book_name))
                full_url = 'https://www.bqg56.com' + n.xpath('./@href').get()
                return full_url
        print('\n未找到该小说名对应的小说资源，请检查小说名是否正确\n')
        novel_url()
    except Exception as e:
        print(e)


def save_chapter(chapter_url, headers, novel_name, tmp):
    chapter_response = requests.get(chapter_url, headers)
    chapter_selector = parsel.Selector(chapter_response.text)
    chapter_title = chapter_selector.xpath('//h1[@class="wap_none"]/text()').get()
    chapter_data = chapter_selector.xpath('//div[@id="chaptercontent"]/text()').getall()
    if not os.path.exists(novel_name):
        os.mkdir(novel_name)
    with open(f'{novel_name}//{tmp}', mode='w', encoding='utf-8') as f:
        print('正在保存 {}\n'.format(chapter_title))
        f.write(chapter_title)
        f.write('\n\n')
        f.write('\n'.join(chapter_data))
        f.write('\n\n\n\n')


def download_novel():
    url = novel_url()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    selector = parsel.Selector(response.text)
    novel_name = selector.xpath('//div[@class="info"]/h1/text()').get()
    dds = selector.xpath('//div[@class="listmain"]/dl//dd')  # 此处要注意是dl下所有的dd标签，//dd，因为网站对中部章节有折叠
    print('准备下载 {}\n'.format(novel_name))
    start_time = time.time()
    no = 1
    res = []
    for dd in dds:
        chapter_url = 'https://www.bqg56.com' + dd.xpath('./a/@href').get()
        tmp = "{0:0>4s}".format(str(no)) + '.txt'
        no += 1
        res.append(tmp)
        try:
            # 此处加try使用异常捕获是因为网站对小说的中部章节会有折叠，可能会报错！
            thread_save_chapter = threading.Thread(target=save_chapter, args=(chapter_url, headers, novel_name, tmp))
            thread_save_chapter.start()
        except Exception as e:
            print(e)
            continue
    while len(threading.enumerate()) > 1:
        time.sleep(1)
    # ret = sorted(res, key=lambda x: int(x[:4]))
    with open(f'{novel_name}//{novel_name}.txt', mode='w+', encoding='utf-8') as f:
        for j in res:
            if os.path.exists(f'{novel_name}//{j}'):
                with open(f'{novel_name}//{j}', mode='r', encoding='utf-8') as ff:
                    f.write(ff.read())
                os.remove(f'{novel_name}//{j}')
    cost_time = time.time() - start_time
    print('\n %s 下载完毕!   总共用时 %s' % (novel_name, cost_time))


if __name__ == '__main__':
    download_novel()
