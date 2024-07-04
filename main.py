# -*- coding: utf-8 -*-
# @Time    : 2024/5/25 16:08
# @Author  : jian lang
# @File    : main.py
# @Description: program entry

import argparse
import os

from crawler import TiktokCrawler
from get_chrome_driver import GetChromeDriver

if __name__ == "__main__":

    print("==> Author: 【Lobster】, master student of UESTC.")

    # Downloading the correct version of ChromeDriver:
    if not os.path.exists('crawler/tools/chromedriver.exe'):
        get_driver = GetChromeDriver()
        get_driver.install(output_path='crawler/tools')
        print('==> ChromeDriver downloaded successfully!')
    else:
        print('==> ChromeDriver already exists! But if the version is not compatible, please delete it and run the '
              'script again.')

    # TikTok Crawler:
    crawler = TiktokCrawler()

    # Crawl the videos from user id given in config/user_id.json
    crawler.crawl_video_info_through_user_id()

