# coding: utf-8

import os
import requests
import json

from .constant import SUB_LAN_URL

def lang_to_blang():
    """
    字幕文件语种和b站字幕语种号的对应关系, 例如en对应en-US
    """
    # 自定义字幕编码的对应关系
    lang2blang = dict()

    langs = [
        "zh-CN",
        "zh-Hans-en",
        "zh-Hans",
        "en"
    ]

    blangs = [
        "zh-CN",
        "zh-CN",
        "zh-Hans",
        "en-US",
    ]

    n = len(langs)
    
    for i in range(n):
        lang2blang[langs[i]] = blangs[i]

    # b站字幕编码的对应关系
    sub_lan = requests.get(SUB_LAN_URL)
    sub_list = json.loads(sub_lan.text)
    for sub in sub_list:
        lang2blang[sub['lan']] = sub['lan']

    return lang2blang

def get_sub_type(subfile):
    """
    获得字幕类型, srt或vtt
    """
    return subfile.split(".")[-1]

def get_sub_lang(subfile):
    """
    获得字幕语种, 例如"zh-Hans", "en"
    """
    return subfile.split(".")[-2]

def get_dir_file(dir):
    """
    获得文件夹中文件
    """
    files = []
    for file in os.listdir(dir):
        new_dir = os.path.join(dir, file)
        if os.path.isdir(new_dir):
            files += get_dir_file(new_dir)
        else:
            files.append(new_dir)
    
    return files

def get_sub_file(dir, sub_type=["srt", "vtt"]):
    """
    获得文件夹中字幕文件
    """
    files = get_dir_file(dir)
    sub_files = []
    for file in files:
        if get_sub_type(file) in sub_type:
            sub_files.append(file)
    
    return sub_files