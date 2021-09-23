# coding: utf-8

"""
代码来自https://github.com/FXTD-ODYSSEY/bilibili-subtile-uploader
"""

import json
import requests

from urllib import parse

from .constant import *

def submit_subtitle(subtitle, oid, csrf, cookie, bvid=None, lang="en-US"):
    """
    提交单个字幕
    """
    subtitle = subtitle if isinstance(subtitle, dict) else {}
    if not subtitle or not oid:
        print(f"{oid} 文件为空 - 跳过")
        return
    subtitle = json.dumps(subtitle)

    payload = f'lan={lang}&submit=true&csrf={csrf}&sign=false&bvid={bvid}&type=1&oid={oid}&{parse.urlencode({"data":subtitle})}'
    headers = {
        # "referer": "https://account.bilibili.com/subtitle/edit/",
        # "origin": "https://account.bilibili.com",
        "Content-Type": "application/x-www-form-urlencoded",
        'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Mobile Safari/537.36"
    }
    headers.update({"Cookie": cookie})

    url = SUB_API
    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def get_bvdata(bvid, url=BVDATA_API):
    """
    获得bv数据
    """
    url += f'?bvid={bvid}'
    response = requests.request("GET", url)

    return json.loads(response.text)

def get_oid(bvdata):
    """
    获得一个bv下的oid(cid)和标题的对应关系, 视频时长的对应关系
    """
    oid_list = {}
    for data in bvdata["data"]["pages"]:
        # cid对应oid, part对应标题名
        oid_list[data["cid"]] = [data["part"], data["duration"]]

    return oid_list

def get_duration(oid_list, oid):
    """
    获得视频时长
    """
    return oid_list[oid][1]

def oid_to_sub(oid_list, sub_files):
    """
    生成oid和本地字幕的对应关系
    """
    oid2sub = dict()
    for oid in oid_list:
        # 得到远程标题
        title = oid_list[oid][0]
        oid2sub[oid] = []
        for subfile in sub_files:
            if title in subfile:
                # 如果本地字幕文件名包含远程标题, 则更新
                oid2sub[oid].append(subfile)
            elif subfile in title:
                # 如果远程标题包含本地字幕, 则更新
                oid2sub[oid].append(subfile)

    return oid2sub