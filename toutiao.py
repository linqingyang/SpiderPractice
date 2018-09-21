# 今日头条
import requests
import json
import os
import pymongo
from hashlib import md5
from urllib.parse import urlencode
from requests.exceptions import RequestException
from selenium import webdriver
from multiprocessing import Pool
from config import *

# 声明数据库对象
client = pymongo.MongoClient(MONGO_URL)
# 声明数据库库名
db = client[MONGO_DB]


def get_index(offset):
    data = {
        "offset": offset,
        "format": "json",
        "keyword": "街拍",
        "autoload": "true",
        "count": "20",
        "cur_tab": "3",
        "from": "gallery",
    }
    url = 'https://www.toutiao.com/search_content/?'+urlencode(data)
    try:
        resp = requests.get(url=url)
        if resp.status_code == 200:
            # print(resp.text)
            return resp.text
        else:
            print("请求出错")
    except RequestException:
        print("出错")


def get_url(page):
    """
    通过得到的json数据得到每篇文章的url
    :param page:
    :return: url
    """
    data = json.loads(page)
    url = data.get("data")
    ll = [i.get("article_url") for i in url]
    return ll


def get_detail(urls):
    info = {}
    for i in urls:
        print(i)
        browser = webdriver.Chrome()
        browser.get(i)
        title = browser.find_element_by_class_name("title").text
        img_urls = browser.find_elements_by_class_name("image-origin")
        for j in img_urls:
            pass
            # download_img(j.get_attribute("href"))
        info.update({
            "title": title,
            "img_url": j.get_attribute("href"),
        })
        browser.quit()

    return info


def download_img(url):
    print('Downloading', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_img(response.content)
        return None
    except ConnectionError:
        return None


def save_img(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    print(file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def save_to_mongo(result):
    """把数据写入数据库中"""
    if db[MONGO_TABLE].insert(result):
        print("写入数据库成功")
        return True
    else:
        print("把{0}存入数据库中失败".format(result))


def main(offset):
    html = get_index(offset)
    urls = get_url(html)
    info = get_detail(urls)
    save_to_mongo(info)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(0, 1 + 1)])
    pool.map(main, groups)
    html = get_index(0)
    pool.close()
    pool.join()
