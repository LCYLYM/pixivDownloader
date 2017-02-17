# -*- coding: utf-8 -*-
import json
from threading import Thread

import redis
import time

from pixiv.PixivPageDownloader import PixivHtmlParser
from pixiv_config import *
from pixivapi.AuthPixivApi import AuthPixivApi
from pixivapi.PixivApi import PixivApi
from pixivapi.PixivUtils import parse_dict
from pixivision.ImageDownload import ImageDownload, IlluDownloadThread
from pixivision.PixivisionDownloader import HtmlDownloader
from utils.MessageHandler import RedisMessageClient, PixivDownloadHandler
from utils.RedisFilter import RedisFilter


def test_pixivision():
    topic_list = HtmlDownloader.parse_illustration_topic(
            HtmlDownloader.download("http://www.pixivision.net/en/c/illustration/?p=1"))
    for topic in topic_list:
        print(topic)
    # 创建特辑文件夹，写入特辑信息。
    href = topic_list[0].href
    illu_list = HtmlDownloader.parse_illustration(HtmlDownloader.download(href))
    for illu in illu_list:
        print(illu)


def test_api():
    detail = PixivApi.illust_detail(54809586)
    print(detail.illust)
    related = PixivApi.illust_related(54809586)
    print(related)


def test_redisFilter():
    r = redis.Redis(REDIS_IP, REDIS_PORT)
    rFilter = RedisFilter(r, 3, "setFilter:Pixivision")
    datas = ["/zh/c/1001", "/zh/c/1002", "/zh/c/1003", "/zh/c/1004", "/zh/c/1005", "/zh/c/1006", "/zh/c/1008",
             "/zh/c/1009"]
    other = "/zh/c/1007"
    rFilter.add_all(datas)
    print(rFilter.is_contained(datas[2]))
    print(rFilter.is_contained(other))
    rFilter.add(other)
    print(rFilter.is_contained(other))
    rFilter.remove(datas[1])
    print(rFilter.is_contained(datas[1]))
    rFilter.remove_all(datas)
    rFilter.remove(other)
    print(rFilter.is_contained(datas[2]))


def test_image_download():
    topics = ImageDownload.get_pixivision_topics("http://www.pixivision.net/en/c/illustration/?p=2",
                                                 IMAGE_SVAE_BASEPATH)
    ts = []
    for topic in topics:
        t = IlluDownloadThread(topic.href, topic.save_path, 1)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


def test_html_parse_byfile():
    html = open("test.html").read()
    print(HtmlDownloader.parse_illustration(html))


def test_pixiv_html_parse_byfile():
    html = open("test.html").read()
    search_result = PixivHtmlParser.parse_search_result(html)
    pop_result = PixivHtmlParser.parse_popular_introduction(html)
    print(search_result)
    print(len(search_result))
    print(pop_result)
    print(len(pop_result))
    print("normal result after filter：")
    search_result = filter(lambda data: data.has_key("mark_count") and int(data.mark_count) > 1000, search_result)
    print(search_result)
    print(len(search_result))


def test_auth_api():
    api = AuthPixivApi("*", "*", access_token="qC-MDpoHtD3ZuN24Ow5LLD-4H3Phs0YtB0S9Dn-E8L0")
    obj = api.search_works("艦これ")
    print(obj)
    resp_page = api.auth_requests_call("get", "http://www.pixiv.net/search.php?word=艦これ&type=illust")
    print(resp_page.content)


# 模拟订阅消息
def test_msg_sub(channel):
    pixiv_api = AuthPixivApi("*", "*")
    handler = PixivDownloadHandler(pixiv_api)
    sub_client = RedisMessageClient(handler)
    sub_client.run_sub(channel)


# 模拟redis消息推送
def test_msg_pub(channel):
    pub_client = RedisMessageClient()
    pub_client.pub(channel, json.dumps({"topic": "download",
                                        "url": "https://i4.pixiv.net/img-original/img/2016/09/13/12/23/34/58959975_p0.jpg"}))
    # pub_client.pub(channel, json.dumps({"topic": "download",
    #                                     "url": "https://i1.pixiv.net/img-original/img/2015/12/27/22/22/00/54279980_p0.jpg"}))
    # pub_client.pub(channel, json.dumps({"topic": "download",
    #                                     "url": "https://i1.pixiv.net/img-original/img/2014/05/28/01/21/50/43748656_p0.jpg"}))
    # pub_client.pub(channel, json.dumps({"topic": "download",
    #                                     "url": "https://i1.pixiv.net/img-original/img/2016/08/20/00/16/23/58541644_p0.png"}))


def download_test(url):
    print("start download:" + str(time.time()))
    PixivApi.download(url)
    # 取最终一个url下载结束时间
    print("url:" + url + " end:" + str(time.time()))


def download_thread_test():
    urls = ["https://i4.pixiv.net/img-original/img/2016/09/13/12/23/34/58959975_p0.jpg",
            "https://i1.pixiv.net/img-original/img/2015/12/27/22/22/00/54279980_p0.jpg",
            "https://i1.pixiv.net/img-original/img/2014/05/28/01/21/50/43748656_p0.jpg",
            "https://i1.pixiv.net/img-original/img/2016/08/20/00/16/23/58541644_p0.png"]
    ts = []
    for url in urls:
        t = Thread(target=download_test, args=(url,))
        t.daemon = True
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


def test_html_parse_byfile_for_search():
    html = open("test.html").read()
    print(PixivHtmlParser.parse_popular_introduction(html))
    print(PixivHtmlParser.parse_search_result(html))


def testbs4():
    from bs4 import BeautifulSoup
    import re
    html = open("test.html").read()
    soup = BeautifulSoup(html)
    lis = soup.find_all("li", class_=re.compile("image-item\s*"))
    datas = []
    for li in lis:
        try:
            url = li.find_all("a", class_=re.compile("work _work\s*"))
            print(url[0])
            data = {"url": PIXIV_URL + li.find_all("a", class_=re.compile("work  _work\w*"), limit=1)[0]['href'],
                    "title": li.find("h1", attrs={"class": "title"}).text}
            # 非关键信息 解析失败不影响主要信息收集
            try:
                user = {}
                user_a = li.find("a", attrs={"class": "user ui-profile-popup"})
                user["name"] = user_a["title"]
                user["id"] = user_a["data-user_id"]
                user["page"] = PIXIV_URL + user_a["href"]
                data["user"] = user
            except Exception, e:
                print("Parse User Warning")
                print(e.message)
            count_a = li.find("a", attrs={"class": "bookmark-count _ui-tooltip"})
            if count_a:
                data["mark_count"] = li.find("a", attrs={"class": "bookmark-count _ui-tooltip"}).text
            else:
                data["mark_count"] = 0
            data = parse_dict(data)
            datas.append(data)
        except Exception, e:
            print("parse_search_result Warning")
            print(e.message)
            continue
    return datas


if __name__ == '__main__':
    print(testbs4())
