# -*- coding: utf-8 -*-
import re

from BeautifulSoup import BeautifulSoup

from pixiv_config import PIXIV_URL
from pixivapi.PixivUtils import parse_dict


class PixivHtmlParser(object):
    # 获取pixiv 插画搜索页搜索结果列表
    @classmethod
    def parse_search_result(cls, html):
        if not html:
            return None
        main = BeautifulSoup(html)
        # 找到搜索结果section
        section = main.find("section", attrs={"class": "column-search-result"})
        # 获取搜索结果中插画
        datas = []
        # 直接搜索section的class失败。则搜索ul 获取image item
        if not section:
            try:
                # 特殊处理首页用推荐的情况
                section = main.find("ul", attrs={"class": "_image-items autopagerize_page_element"})
                if not section:
                    print("search normal result is empty")
                    return datas
            except:
                print("search normal result is empty")
                return datas
        lis = section.findAll("li", attrs={"class": re.compile("image-item\s*")})
        if not lis:
            try:
                # 特殊处理首页用推荐的情况
                uls = main.findAll("ul", attrs={"class": "_image-items autopagerize_page_element"})
                if len(uls) >= 2:
                    ul = uls[1]
                    lis = ul.findAll("li", attrs={"class": re.compile("image-item\s*")})
                if not lis:
                    print("search normal result is empty")
                    return datas
            except:
                print("search normal result is empty")
                return datas
        for li in lis:
            try:
                data = {"url": PIXIV_URL + li.find("a",
                                                   attrs={"class": re.compile("work  _work\w*")})["href"],
                        "title": li.find("h1", attrs={"class": "title"}).text}
                # 非关键信息 解析失败不影响主要信息收集
                try:
                    user = {}
                    user_a = li.find("a", attrs={"class": "user ui-profile-popup"})
                    user["name"] = user_a["title"]
                    user["id"] = user_a["data-user_id"]
                    user["page"] = PIXIV_URL + user_a["href"]
                    data["user"] = user
                except Exception as e:
                    print("Parse User Warning")
                    print(e.message)
                count_a = li.find("a", attrs={"class": "bookmark-count _ui-tooltip"})
                if count_a:
                    data["mark_count"] = li.find("a", attrs={"class": "bookmark-count _ui-tooltip"}).text
                else:
                    data["mark_count"] = 0
                data = parse_dict(data)
                datas.append(data)
            except Exception as e:
                print("parse_search_result Warning")
                print(e.message)
                continue
        return datas

    # 获取pixiv搜索页，热门作品列表
    @classmethod
    def parse_popular_introduction(cls, html):
        if not html:
            return None
        main = BeautifulSoup(html)
        section = main.find("section", attrs={"class": "popular-introduction"})
        datas = []
        if not section:
            print("search popular result is empty")
            return datas
        lis = section.findAll("li", attrs={"class": re.compile("image-item\s*")})
        if not lis:
            print("search popular result is empty")
            return datas
        for li in lis:
            try:
                data = {"url": PIXIV_URL + li.find("a", attrs={"class": re.compile("work  _work\w*")})["href"],
                        "title": li.find("h1", attrs={"class": "title"}).text}
                data = parse_dict(data)
                datas.append(data)
            except Exception as e:
                print("parse_popular_introduction Warning:")
                print(e.message)
                continue
        return datas
