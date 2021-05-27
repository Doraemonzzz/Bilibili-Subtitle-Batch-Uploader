# coding: utf-8

import os
import sys
import configargparse as argparse

from .constant import CONF_FILE_NAME

def parse_args():
    """
    解析命令行参数
    """
    parse_kwargs = dict()

    conf_file_path = os.path.join(os.getcwd(), CONF_FILE_NAME)
    if os.path.isfile(conf_file_path):
        parse_kwargs["default_config_files"] = [conf_file_path]
    parser = argparse.ArgParser(**parse_kwargs)

    # 基本参数
    parser.add_argument(
        "--sub_dir",
        dest="sub_dir",
        action='store',
        default=None,
        help="字幕地址"
    )

    parser.add_argument(
        "--bvid",
        dest="bvid",
        action='store',
        default=None,
        help="视频bv号"
    )

    parser.add_argument(
        "--csrf",
        dest="csrf",
        action='store',
        default=None,
        help="CSRF Token"
    )

    parser.add_argument(
        "--cookie",
        dest="cookie",
        action='store',
        default=None,
        help="Cookie"
    )

    # 解析参数
    args = parser.parse_args()

    return args
    