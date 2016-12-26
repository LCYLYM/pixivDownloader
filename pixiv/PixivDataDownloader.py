# -*- coding: utf-8 -*-
import re

import requests

from pixiv.PixivPageDownloader import PixivHtmlParser
from pixiv_config import PIXIV_LOGIN_KEY, PIXIV_PAGE_HEADERS, PIXIV_LOGIN_URL, RETRY_TIME, TIMEOUT, PIXIV_SEARCH_URL, \
    DOWNLOAD_THRESHOLD
from pixivapi.PixivUtils import parse_resp, PixivError


def get_post_key(content):
    if content:
        postkey_str = re.search('name="post_key" value="\w*"', content)
        if postkey_str:
            return postkey_str.group().split('"')[-2]
    else:
        return None


class PixivDataHandler(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.login()

    # 模拟页面登录pixiv
    def login(self):
        r = self.session.get(PIXIV_LOGIN_KEY, headers=PIXIV_PAGE_HEADERS)
        if r.ok:
            post_key = get_post_key(r.content)
            if post_key:
                post_data = {
                    'pixiv_id': self.username,
                    'password': self.password,
                    'post_key': post_key,
                    'source': 'accounts'
                }
            response = self.session.post(PIXIV_LOGIN_URL, data=post_data, headers=PIXIV_PAGE_HEADERS)
            res_obj = parse_resp(response)
            if res_obj.body.has_key("successed"):
                return self.session
            else:
                raise PixivError('username or password wrong!.')
        else:
            print('get post_key error')

    # 获取pixiv页面
    def request_page(self, url, encoding='utf-8'):
        count = 0  # 失败重试次数
        while count <= RETRY_TIME:
            try:
                r = self.session.get(url=url, headers=PIXIV_PAGE_HEADERS, timeout=TIMEOUT)
                r.encoding = encoding
                if (not r.ok) or len(r.content) < 300:
                    count += 1
                    continue
                else:
                    return r.text
            except Exception:
                count += 1
                continue
        return None

    def search(self, word, page=1, type='illust'):
        if word:
            url = (PIXIV_SEARCH_URL % (word, page, type))
        else:
            raise PixivError('search word can not be null')
        html = self.request_page(url)
        # 过滤收藏数不超过 阈值的插画信息
        search_result = filter(PixivHtmlParser.parse_search_result(html),
                               lambda data: data.has_key("mark_count") and data.mark_count > DOWNLOAD_THRESHOLD)
        pop_result = PixivHtmlParser.parse_popular_introduction(html)
        return search_result.append(pop_result)


