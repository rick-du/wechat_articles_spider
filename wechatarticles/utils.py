# coding: utf-8
"""
辅助脚本函数
"""
import html
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup as bs

from .GetUrls import PCUrls

base_columns = ['url', 'title', 'date', 'headlines', 'copyright']
A_columns = ['read_num', 'old_like_num', 'like_num']
B_columns = ['comments_num', 'comments_content', 'comments_like_num']
C_columns = ['content', 'content_num', 'pic_num']
mode_columns = {
    1: A_columns,
    2: B_columns,
    3: C_columns,
    4: A_columns + B_columns,
    5: A_columns + C_columns,
    6: B_columns + C_columns,
    7: A_columns + B_columns + C_columns
}

ctext = '你的访问过于频繁，需要从微信打开验证身份，是否需要继续访问当前页面'


# url, readnum likenum
def flatten(x):
    return [y for l in x for y in flatten(l)] if type(x) is list else [x]


def remove_duplicate_json(fname):
    # 删除json中重复的数据
    # fname: xxx.json
    with open(fname, 'r', encoding='utf-8') as f:
        data = f.readlines()

    id_re = re.compile(r'datetime": (.+), "fakeid"')
    sort_func = lambda line: id_re.findall(line)[0]

    list_data = list(set(data))
    sort_data = sorted(list_data, key=sort_func)[::-1]

    # sort_data = sorted(list(set_data),
    #                    key=lambda line: re.findall(
    #                        r'datetime": (.+), "fakeid"', line)[0])[::-1]

    with open(fname, 'w', encoding='utf-8') as f:
        f.writelines(sort_data)


def end_func(timestamp, end_timestamp):
    if timestamp < end_timestamp:
        print(timestamp, end_timestamp)
        return True
    return False


def transfer_url(url):
    url = html.unescape(html.unescape(url))
    return eval(repr(url).replace('\\', ''))


def save_f(fname):
    i = 1
    while True:
        if os.path.isfile('{}.json'.format(fname)):
            i += 1
            fname += '-' + str(i)
        else:
            break

    return fname


# verify_lst = ["mp.weixin.qq.com", "__biz", "mid", "sn", "idx"]
verify_lst = ["mp.weixin.qq.com", "__biz", "mid", "idx"]


def verify_url(article_url):
    for string in verify_lst:
        if string not in article_url:
            return False
    return True


def get_content(url, cookie):
    headers = {
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        'cookie': cookie
    }
    html_text = requests.get(url.strip(), headers=headers).text

    soup = bs(html_text, 'lxml')
    if ctext in html_text:
        assert 1 == 2
    # js加载
    # html.text.split('var content = ')[1].split('var')[0].strip()
    # soup.find(id="js_panel_like_title").text
    try:
        body = soup.find(class_="rich_media_area_primary_inner")
        content_p = body.find(class_="rich_media_content")
        if content_p:
            imgs = body.find_all('img')
            return content_p.text.strip(), len(
                content_p.text.strip()), len(imgs)
        else:
            content_p = soup.find(id="js_panel_like_title").text.strip()
            return content_p, len(content_p), 0
        # with open(txt_name, 'w', encoding='utf-8') as f:
        # f.write(content_p.text)
    except:
        return '', 0, 0


def copyright_num(copyright_stat):
    if copyright_stat == 11:
        return 1  # 标记原创
    else:
        return 0


def copyright_num_detailed(copyright_stat):
    copyright_stat_lst = [14, 12, 201]
    if copyright_stat == 11:
        return 1  # 标记原创
    elif copyright_stat == 100:
        return 0  # 荐号
    elif copyright_stat == 101:
        return 2  # 转发
    elif copyright_stat == 0:
        return 3  # 来源非微信文章
    elif copyright_stat == 1:
        return 4  # 形容词（xxx的公众号）
    elif copyright_stat in copyright_stat_lst:
        return 5
    else:
        return None


def read_nickname(fname):
    # 读取数据
    with open(fname, 'r', encoding='utf-8') as f:
        haved_data = f.readlines()
    return [line.split(', ') for line in haved_data]


def get_history_urls(biz,
                     uin,
                     key,
                     lst=[],
                     start_timestamp=0,
                     count=10,
                     endcount=99999):
    t = PCUrls(biz=biz, uin=uin, cookie='')
    try:
        while True:
            res = t.get_urls(key, offset=count)
            if res == []:
                break
            count += 10
            print(count)
            lst.append(res)
            dt = res[-1]["comm_msg_info"]["datetime"]
            if dt <= start_timestamp or count >= endcount:
                break
            time.sleep(5)
    except KeyboardInterrupt as e:
        print('程序手动中断')
        return lst
    except Exception as e:
        print(e)
        print("获取文章链接失败。。。退出程序")
        assert 1 == 2
    finally:
        return lst
