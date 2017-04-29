#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-4-29 下午4:03
# @Author  : Sylor
# @File    : meizian.py
# @Software: PyCharm

import requests
from bs4 import BeautifulSoup
import os
from multiprocessing import Pool
from  config  import *
import pymongo

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

def response(all_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'}
        response_a = requests.get(all_url,headers=headers)
        if response_a.status_code == 200:
            return response_a
        else:
            print('链接错误')
    except:
        return None

def get_html(all_url):
    try:
        html = response(all_url)
        all_a= BeautifulSoup(html.text,'lxml').find('div',class_='gallery galleryindex').find_all('a')
        for a in all_a:
            data = {
                'title': a.img.attrs['alt'],
                'link': 'http://meizian.com'+a.attrs['href']
            }
            parse_html = data['link']
            path = data['title'].replace("/", '_')
            print('正在创建文件夹')
            mkdir(path)
            parse_index(parse_html)
            save_to_mongo(data)
    except:
        return None

def parse_index(parse_html):
    page_content = response(parse_html)
    page_a = BeautifulSoup(page_content.text,'lxml').find('div',class_='text-center').find_all('a')[:-2]
    for a in page_a:
        page_html = 'http://meizian.com' + a['href']
        img_html(page_html)

def img_html(page_html):
    parse_content = response(page_html)
    img_a = BeautifulSoup(parse_content.text,'lxml').find('div',id='gallery').find_all('a')
    for a in img_a:
        imgs = a['href']
        print(imgs)
        print('正在准备保存图片')
        save_img(imgs)

def save_img(imgs):
    img = response(imgs)
    name = imgs[-12:-4]
    f=open(name+'.jpg','ab')
    f.write(img.content)
    f.close()
    print('保存完毕')

def save_to_mongo(data):
    if db[MONGO_TABLE].insert(data):
        print('存储到MongoDB成功')
        return True

def mkdir(path):
    path = path.strip()
    os.makedirs(os.path.join("/opt/meizian2",path))
    os.chdir(os.path.join("/opt/meizian2/"+path))


def main(p):
    all_url = 'http://meizian.com/meitui.html' + '?p=' +str(p)
    get_html(all_url)


if __name__ == '__main__':
    pool = Pool()
    pool.map(main,[p for p in range(1,76)])



