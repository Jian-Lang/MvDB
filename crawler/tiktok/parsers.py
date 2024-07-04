# -*- coding: utf-8 -*-
# @Time    : 2024/2/26 9:12
# @Author  : jian lang
# @File    : parsers.py
# @Description: parse data from yaml file

import argparse
import yaml


def load_yaml(path):

    with open(path, 'r') as f:

        config = yaml.safe_load(f)

    return config


def build_parser(mode):

    parser = argparse.ArgumentParser()

    if mode == 'video_info':

        config = load_yaml(r'config/tiktok/video_info.yaml')

        parser.add_argument('--init_date', default=config['CRAWLER']['INIT_DATE'], type=str, help='initial date of crawling, earlier than this date will not be crawled')
        parser.add_argument('--max_comments', default=config['CRAWLER']['MAX_COMMENTS'], type=int, help='maximum number of comments to crawl')
        parser.add_argument('--save_path', default=config['CRAWLER']['SAVE_PATH'], type=str, help='path to save the crawled data')

    return parser


if __name__ == '__main__':

    parser = build_parser('uid2video')

    args = parser.parse_args()

    print(args)
