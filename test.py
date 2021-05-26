# import pysrt

# subs = pysrt.open(r"C:\Users\qinzhen\Desktop\公开课搬运\srt\sub\[2018-01-17] Lecture 1. Introduction to Probabilistic Graphical Models Terminology and Examples.zh-Hans-en.srt")

# for sub in subs:
#     print(sub.text)
#     break

from cmd import parse_args
from bcc_parser import BccParserMixin

import json

def args_test():
    args = parse_args()

    print(args.sub_dir)
    print(args.bvid)
    print(args.csrf)
    print(args.cookie)

def sub_parser_test(srt_path):
    print(srt_path)
    bcc_parser = BccParserMixin()
    filename = "tmp.json"
    print(bcc_parser.srt2bcc(srt_path))
    with open(filename, "w") as f:
        f.write(json.dumps(bcc_parser.srt2bcc(srt_path)))

def main():
    args_test()
    # sub_parser_test("./test_subtitle/[2018-04-03] Lecture 17 Variational Algorithms for Approximate Bayesian Inference Linear Regression.en.srt")
    sub_parser_test(r"D:\MOOC\sub\280A\[2020-12-11] 19.2 Renewal Theory.zh-Hans-en.srt")
    # pass

if __name__ == '__main__':
    main()