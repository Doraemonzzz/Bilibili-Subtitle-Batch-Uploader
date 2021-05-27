import json

from cmd import parse_args
from bcc_parser import BccParserMixin

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
    # args_test()
    # sub_parser_test("[2018-04-03] Lecture 17 Variational Algorithms for Approximate Bayesian Inference Linear Regression.en.srt")
    pass

if __name__ == '__main__':
    main()