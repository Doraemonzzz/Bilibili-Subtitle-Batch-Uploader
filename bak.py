# coding: utf-8

import os
import re
import sys
import json
import copy
import random
import tempfile
import requests
import contextlib
import subprocess
from datetime import datetime
from urllib import parse

import pysrt
import pyvtt

class BccParserMixin(object):
    @staticmethod
    def srt2bcc(srt_path):
        """srt2bcc 将 srt 转换为 bcc B站字幕格式
        :param srt_path: srt 路径
        :type srt_path: srt
        :return: bcc json 数据
        :rtype: srt
        """
        subs = pysrt.open(srt_path)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": [
                {
                    "from": sub.start.ordinal / 1000,
                    "to": sub.end.ordinal / 1000,
                    "location": 2,
                    "content": sub.text,
                }
                for sub in subs
            ],
        }
        return bcc if subs else {}

    @staticmethod
    def vtt2bcc(path, threshold=0.1, word=True):
        path = path if path else ""
        if os.path.exists(path):
            subs = pyvtt.open(path)
        else:
            subs = pyvtt.from_string(path)

        caption_list = []
        if not word:
            caption_list = [
                {
                    "from": sub.start.ordinal / 1000,
                    "to": sub.end.ordinal / 1000,
                    "location": 2,
                    "content": sub.text_without_tags.split("\n")[-1],
                }
                for sub in subs
            ]
        else:
            # NOTE 按照 vtt 的断词模式分隔 bcc
            for i, sub in enumerate(subs):
                text = sub.text

                start = sub.start.ordinal / 1000
                end = sub.end.ordinal / 1000
                try:
                    idx = text.index("<")
                    pre_text = text[:idx]
                    regx = re.compile(r"<(.*?)><c>(.*?)</c>")
                    for t_str, match in regx.findall(text):
                        pre_text += match
                        t = datetime.strptime(t_str, r"%H:%M:%S.%f")
                        sec = (
                            t.hour * 3600
                            + t.minute * 60
                            + t.second
                            + t.microsecond / 10 ** len((str(t.microsecond)))
                        )
                        final_text = pre_text.split("\n")[-1]

                        if caption_list and (
                            sec - start <= threshold
                            or caption_list[-1]["content"] == final_text
                        ):
                            caption_list[-1].update(
                                {
                                    "to": sec,
                                    "content": final_text,
                                }
                            )
                        else:
                            caption_list.append(
                                {
                                    "from": start,
                                    "to": sec,
                                    "location": 2,
                                    "content": final_text,
                                }
                            )
                        start = sec
                except:
                    final_text = sub.text.split("\n")[-1]
                    if caption_list and caption_list[-1]["content"] == final_text:
                        caption_list[-1].update(
                            {
                                "to": end,
                                "content": final_text,
                            }
                        )
                    else:
                        if caption_list and end - start < threshold:
                            start = caption_list[-1]["to"]
                        caption_list.append(
                            {
                                "from": start,
                                "to": end,
                                "location": 2,
                                "content": final_text,
                            }
                        )

        # NOTE 避免超出视频长度
        last = caption_list[-1]
        last["to"] = last.get("from") + 0.1
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": caption_list,
        }

        return bcc if subs else {}

def submit_subtitle(subtitle, oid, bvid=None, lang="en-US"):
    subtitle = subtitle if isinstance(subtitle, dict) else {}
    if not subtitle or not oid:
        print(f"{oid} 文件为空 - 跳过")
        return
    subtitle = json.dumps(subtitle)

    csrf = "7782f82ccd52bda4727d1158367b3979"
    payload = f'lan={lang}&submit=true&csrf={csrf}&sign=false&bvid={bvid}&type=1&oid={oid}&{parse.urlencode({"data":subtitle})}'

    headers = {
        # "referer": "https://account.bilibili.com/subtitle/edit/",
        # "origin": "https://account.bilibili.com",
        "Content-Type": "application/x-www-form-urlencoded",
        'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Mobile Safari/537.36"
    }
    headers.update({"Cookie": "_uuid=C2093CB0-8345-F808-BEEC-47D5A16AC23F79328infoc; buvid3=38167AB7-3A5F-4A90-8FB8-0644518A555A34762infoc; sid=5lvejh9x; DedeUserID=291079982; DedeUserID__ckMd5=039c4f26979407d9; SESSDATA=ec02c5b3%2C1635993230%2C7f464*51; bili_jct=7782f82ccd52bda4727d1158367b3979; CURRENT_FNVAL=80; blackside_state=1; rpdid=|(umYkk~mRuu0J'uYk|YJ|RYu; bp_t_offset_291079982=524127134157512045; buvid_fp=38167AB7-3A5F-4A90-8FB8-0644518A555A34762infoc; buvid_fp_plain=38167AB7-3A5F-4A90-8FB8-0644518A555A34762infoc; bsource=search_google; bp_video_offset_291079982=528317265593533881; fingerprint3=8f980d546246aaeaf2aa9bc25dafa3a4; fingerprint=c038b805010b1f20e2c817f2cb9eb780; fingerprint_s=47878742ba663e7e411dcd977e21d236; PVID=2"})

    url = "https://api.bilibili.com/x/v2/dm/subtitle/draft/save"
    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def get_bvdata(bvid, url="http://api.bilibili.com/x/web-interface/view"):
    url = "http://api.bilibili.com/x/web-interface/view" + f'?bvid={bvid}'
    response = requests.request("GET", url)

    return json.loads(response.text)

def get_oid(bvdata):
    oid_list = {}
    for data in bvdata["data"]["pages"]:
        oid_list[data["cid"]] = data["part"]

    return oid_list

def suffix2lang():
    # "lan_doc":"中文（中国）", "lan_doc":"中文（简体）"
    lang_list = [
        "zh-CN",
        "zh-Hans",
        "en-US",
    ]

    suffix = [
        "zh-Hans-en",
        "zh-Hans",
        "en"
    ]

    suf2lang = dict()
    for i in range(3):
        suf2lang[suffix[i]] = lang_list[i]

    return lang_list, suffix, suf2lang

def subtype(subfile):
    return subfile.split(".")[-1]

def sublang(subfile):
    return subfile.split(".")[-2]

def main():
    lang_list, suffix, suf2lang = suffix2lang()
    # par
    sub_dir = r"D:\MOOC\视频\字幕合集\待上传\CS50's Introduction to Game Development 2018"
    bvid = "1Q64y1d76q"
    lang = "en-US"
    oid = "332771577"
    bvdata = get_bvdata(bvid)
    oid_list = get_oid(bvdata)
    
    # get sub_files
    sub_files = []
    for file in os.listdir(sub_dir):
        if file.split(".")[-1] in ["vtt", "srt"]:
            sub_files.append(file)

    # sub parser
    subParser = BccParserMixin()
    #subtitle = subParser.srt2bcc("/Users/qinzhen/Desktop/学习/web/srt/1.srt")

    # generate oid's subtitle
    oid2sub = dict()
    for oid in oid_list:
        title = oid_list[oid]
        oid2sub[oid] = []
        for subfile in sub_files:
            if title in subfile:
                #print(title, subfile)
                oid2sub[oid].append(subfile)

    # upload subtitle
    for oid in oid_list:
        zh_en_flag = 0
        for subfile in oid2sub[oid]:
            filepath = os.path.join(sub_dir, subfile)
            srttype = subtype(filepath)
            sublangtype = sublang(filepath)
            lang = suf2lang[sublangtype]
            # for suff in suffix:
            #     lang = suf2lang[suff]
            #     # getfile
            #     if suff in filepath:
            #         break
            
            # generate bilibili subtitle
            if subtype(subfile) == "vtt":
                subtitle = subParser.vtt2bcc(filepath)
            else:
                subtitle = subParser.srt2bcc(filepath)

            # judge whether to upload zh-Hans subtitle
            # print(lang, zh_en_flag)
            # if (sublangtype == "zh-Hans") and (zh_en_flag == 1):
            #     continue

            # get response
            response = submit_subtitle(subtitle, oid, bvid, lang)
            print(response)
            # if (sublangtype == "zh-Hans-en") and (response["code"] == 0):
            #     zh_en_flag = 1
            print(filepath, lang, sublangtype)
            #submit_subtitle(subtitle, oid, bvid, lang)
            #code
            

    #print(oid_list)
    #print(oid2sub[332774696])
    
    #print(sub_files)


    print("Hello, world")


    #print(oid_list)

    #print(return_data)
    #print(return_data.keys())
    #print(return_data)



    #print(submit_subtitle(subtitle, oid, bvid, lang))

if __name__ == "__main__":
    main()