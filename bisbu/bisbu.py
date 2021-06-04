# coding: utf-8

import os
import re
import sys
import json
import copy
import random
import tempfile
import contextlib
import subprocess

from datetime import datetime
from tqdm import tqdm

from .cmd import parse_args
from .bilibili_tool import submit_subtitle, get_bvdata, get_oid, oid_to_sub, get_duration
from .sub_tool import lang_to_blang, get_sub_type, get_sub_lang, get_sub_file
from .bcc_parser import BccParserMixin

def gen_fail_upload(fail_upload, output="fail_upload.txt"):
    """
    生成上传失败的字幕列表
    """
    with open(output, "w") as f:
        for file in fail_upload:
            f.writelines(file + "\n")

def main():
    # 参数
    args = parse_args()
    sub_dir = args.sub_dir
    bvid = args.bvid
    csrf = args.csrf
    cookie = args.cookie
    lang2blang = lang_to_blang()
    bvdata = get_bvdata(bvid)
    oid_list = get_oid(bvdata)
    
    # 获得字幕绝对路径
    sub_files = get_sub_file(sub_dir)

    # sub parser
    subParser = BccParserMixin()

    # oid和本地字幕的对应关系
    oid2sub = oid_to_sub(oid_list, sub_files)

    # 上传字幕
    fail_upload = []
    for oid in tqdm(oid_list):
        # 时长
        duration = get_duration(oid_list, oid)
        for subfile in oid2sub[oid]:
            # 字幕类型
            sub_type = get_sub_type(subfile)
            # 字幕语种
            lang = get_sub_lang(subfile)
            # 字幕对应的b站语种代码
            blang = lang2blang[lang]
            
            # 判断字幕类型
            if sub_type == "vtt":
                subtitle = subParser.vtt2bcc(subfile, duration)
            else:
                subtitle = subParser.srt2bcc(subfile, duration)

            # 获得响应
            response = submit_subtitle(subtitle, oid, csrf, cookie, bvid, blang)
            if (response["code"] != 0):
                fail_upload.append(subfile)

    # 记录上传失败的字幕
    output = os.path.join(sub_dir, "fail_upload.txt")
    gen_fail_upload(fail_upload, output)

    # 生成上传情况
    if (len(output) == 0):
        print("字幕全部上传成功!")
    else:
        print(f"字幕部分上传失败，上传失败的字幕名称保存在{output}，共{len(output)}个！")

if __name__ == "__main__":
    main()