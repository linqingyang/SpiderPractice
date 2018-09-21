# requests库结合正则表达式 爬取猫眼电影榜单信息
import requests
from requests.exceptions import RequestException
import re
import json
from multiprocessing import Pool
import time


def get_film_html(url):
    """
    根据传入的网址得到网页的html代码
    :param url: 传入目标网址
    :return: 解析的html
    """
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'maoyan.com',
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://maoyan.com/board',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.36 '
    }
    try:
        resp = requests.get(url=url, headers=headers)
        if resp.status_code == 200:
            return resp.text
        else:
            print("网页解析出错了")
    except RequestException:
        return "出错了"


def passer_page(page):
    """解析页面"""
    print("Hello")
    dic = {}
    pattern = re.compile(
        '<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">.*?(.*?)'
        '</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',
        re.S)
    ll = re.findall(pattern, page)
    for item in ll:
        yield {
            "index": item[0],
            "img-src": item[1],
            "name": item[2],
            "actors": item[3].strip()[3:],
            "time": item[4].strip()[5:],
            "score": item[5]+item[6]
        }


def save_to_file(text):
    """保存文件存成txt类型"""
    with open("top100.txt", "a", encoding='utf-8') as f:
        f.write(json.dumps(text, ensure_ascii=False) + "\n")
        f.close()


def main(offset):
    url = "http://maoyan.com/board/4?offset=" + str(offset)
    html = get_film_html(url)
    for j in passer_page(html):
        save_to_file(j)


if __name__ == '__main__':
    start = time.time()
    pool = Pool()
    pool.map(main, [i for i in range(0, 91, 10)])
    end = time.time()
    print("抓取前100部电影共耗时：{0}秒".format(end-start))





