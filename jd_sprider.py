#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/22 15:38
import re
import time
import pymongo
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jd_config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
wait = WebDriverWait(browser, 4)
# 设置浏览器大小
browser.set_window_size(1400, 900)


def search_get():
    """
    得到搜索页面

    """
    browser.get("https://www.jd.com/")
    try:
        print("正在进行关键词搜索")
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#key"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button"))
        )
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1)"))
        )
        get_info()
        return total.text
    except TimeoutException:
        print('请求出错正在重连')
        return search_get()
    finally:
        pass


def get_next_page(page_number):
    """根据传入的number开始下一页"""
    try:
        print("正在进行翻页", page_number)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next > em'))
        )
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.curr'), str(page_number)))
        get_info()
    except TimeoutException:
        return get_next_page(page_number)


def get_info():
    """每一项商品的详细信息
        xmlns="http://www.w3.org/1999/xhtml"这个属性会导致pyquery.find不正确 困扰了好久
    """
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_goodsList > ul")))
    html = browser.page_source
    doc = pq(html.replace('xmlns', 'sss'))
    print("正在得到当前页面的商品信息")
    items = doc('#J_goodsList .gl-warp .gl-item .gl-i-wrap ').items()
    # print(items)
    for i in items:
        info = {}
        ll = i('.p-img').find('img')
        if ll.attr('data-lazy-img') == 'done':
            info['img'] = ll.attr('src')
        else:
            info['img'] = ll.attr('data-lazy-img')
        info['name'] = i('.p-name').find('em').text().replace('\n', '')
        info['price'] = i('.p-price').find('i').text()
        info['commit'] = i('.p-commit').find('a').text()
        info['shop'] = i('.p-shop .J_im_icon').find('a').text()
        # print(info)
        save_to_mongo(info)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print("保存数据到MongoDB中成功")
        else:
            print("保存数据到MongoDB中失败!!!", result)
    except pymongo.errors.DuplicateKeyError:
        print("存在id重复冲突ToT")


def main():
    try:
        all = search_get()
        all = int(re.search(r'\d+', all).group())
        for i in range(2, all+1):
            get_next_page(i)
    except Exception:
        print("爬取过程出现异常")
    finally:
        browser.close()


if __name__ == '__main__':
    main()