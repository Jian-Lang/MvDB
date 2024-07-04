# -*- coding: utf-8 -*-
# @Time    : 2024/3/5 9:12
# @Author  : jian lang
# @File    : utils.py
# @Description: functional tools assisting the crawling process

import logging
import os
import time
from datetime import datetime

import colorlog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def check_dirs_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"==> {path} does not exist and has been created!")


def init_browser(path):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_extension(r'D:\MVDB\ublock.crx')
    browser = webdriver.Chrome(path, chrome_options=options)
    # rawdata = "tt_csrf_token=Lro1sFmD-ynBrlAIwVD9WXEhJwLl1dgsg8Cc; tt_chain_token=CA+DqOiMT1jFzRT5pPlI4g==; ak_bmsc=28D04996972202CCB7A3EE9A66CA889E~000000000000000000000000000000~YAAQvlA7F239RKSPAQAAeiOuzRcWvb5EvUmMYQLb/luC55lhMhW1pW3CYFrLhcpo+9z4L/rI70h6UZMLLE0Q3JT6XFHelRAROoE59dI0oprulKm4CWGhDl0tFbv5i/u2BNO5No3AupEtqAQ93iQ+WsdDu64Rj1BaQZNdWjvbh3/clWUtsBjkRZLeDElatOO+G2+ID26vDybuv1S52m+3hZablpMR+rF1hdmiwr/UH+w3qJZcuN9+umFjAvv4cagtduTPQZXZERRW24JC/oAJrp8XQmDvEaF8bGKNO/iafLRyP+1R2ypfjPvINgGfNFDJhAmplJrwZNfsBa3sgM25Kmm2TLS161J1Xxg32Aoab8Zy098ukZCIRVos3XpaSjm0aLPluclC5in9nA==; tiktok_webapp_theme=light; ttwid=1%7CQ65enVfxXeO_bWO2CTstCxVCfmk4G5eEf8JNQHEHMO0%7C1717142694%7Cfbabcf9251d4dfb436de005490bab5b0aa7e507d61670e0186c5db995f7a5eba; odin_tt=b15500ee97848a4bfbc326f77e152f77d7bcd65ceb919ac373ba5bdb99422d8b641d179982607dfa50e5a6474a002a1ee4739153747789e1516e5c2a16fbe6397f1f670c1ca99bdab9c308ba00fdc10c; passport_csrf_token=076b98975d58d949344a9783551a59d8; passport_csrf_token_default=076b98975d58d949344a9783551a59d8; perf_feed_cache={%22expireTimestamp%22:1717315200000%2C%22itemIds%22:[%227364799744012455174%22%2C%227374345117697838341%22%2C%227360199461563370768%22]}; bm_sv=745EB59C19492B3EAF4AD9644FD49775~YAAQvlA7Fxv+RKSPAQAATj6uzRfBDkSkdY7jx/8MPgC9ncOfzP1zW5M3lCqL5pP0vZKpbJoClJU4DL695VOZecbLwaLi95soGO5vUl6oO25443Il0Ruqmwb2swvYnIhQw17eZ6RpH/Ar2ntVCIDFg/xvINlxBcUmOWEJobG5IvKbTHbeNbAXMGo6e2+e1hEzq3Pkp8mC+ytfVg2Rd+U9K0NVEEKWAEGLT4ylRcDXV7tY+tUn7I9eJGSXR6jXAkKz~1; msToken=jjlFF8qYRAN_IxQakIMC2mwXGjkwmKDXRz2wkunNf0y9ab6u1cwssPABBG-_8wkjpSa6KZ2XY8_F1PxRKMnyqYewc48Y3H_Miw_tjTnQhdYpx_Di16HsQXYcx6B2NT59ioTtnTDVNGxEuxaJ91wxseM=; msToken=jjlFF8qYRAN_IxQakIMC2mwXGjkwmKDXRz2wkunNf0y9ab6u1cwssPABBG-_8wkjpSa6KZ2XY8_F1PxRKMnyqYewc48Y3H_Miw_tjTnQhdYpx_Di16HsQXYcx6B2NT59ioTtnTDVNGxEuxaJ91wxseM="
    # cookie = SimpleCookie()
    # cookie.load(rawdata)
    # # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # # which is incompatible with requests. Manually construct a dictionary instead.
    # cookies = {k: v.value for k, v in cookie.items()}

    return browser

def solve_popup(browser):
    button_visitors = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1cp64nz-DivTextContainer')))
    button_visitors[4].click()


def make_logger(path):
    # 配置日志记录
    # 创建logger对象
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    # 创建文件处理器
    file_handler = logging.FileHandler(os.path.join(path, f'log.txt'))
    file_handler.setLevel(logging.INFO)
    # 设置日志格式
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'yellow',
            'INFO': 'yellow',
            'WARNING': 'yellow',
            'ERROR': 'yellow',
            'CRITICAL': 'yellow',
        }
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # 将处理器添加到logger对象中
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def convert_date(init_date):
    current_date = time.strftime("%Y-%m-%d", time.localtime())
    if "天前" in init_date:
        days = int(init_date.split("天前")[0])
        date = (time.strptime(current_date, "%Y-%m-%d"))
        timestamp = time.mktime(date) - days * 24 * 3600
        date = time.strftime("%Y-%m-%d", time.localtime(timestamp))
    elif "小时前" in init_date:
        hours = int(init_date.split("小时前")[0])
        timestamp = time.time() - hours * 3600
        date = time.strftime("%Y-%m-%d", time.localtime(timestamp))
    elif "分钟前" in init_date:
        minutes = int(init_date.split("分钟前")[0])
        timestamp = time.time() - minutes * 60
        date = time.strftime("%Y-%m-%d", time.localtime(timestamp))
    elif "周前" in init_date:
        weeks = int(init_date.split("周前")[0])
        date = (time.strptime(current_date, "%Y-%m-%d"))
        timestamp = time.mktime(date) - weeks * 7 * 24 * 3600
        date = time.strftime("%Y-%m-%d", time.localtime(timestamp))
    else:
        date = "2024-" + init_date
    return date


def compare_dates(date1, date2):
    """
    Compare two dates.
    Args:
    date1 (str): The first date string in the format "YYYY-MM-DD".
    date2 (str): The second date string in the format "YYYY-MM-DD".
    Returns:
    int: 0 if date1 equals date2, -1 if date1 is before date2, 1 if date1 is after date2.
    """
    date1_obj = datetime.strptime(date1, "%Y-%m-%d")
    date2_obj = datetime.strptime(date2, "%Y-%m-%d")
    if date1_obj == date2_obj:
        return 0
    elif date1_obj < date2_obj:
        return -1
    else:
        return 1


if __name__ == "__main__":
    # print(date_convert("57分钟前"))
    pass
    # big_v = {
    #     "sports": "haessik",
    #     "anime_manga": "vidztoker",
    #     "love_relationships": "crzanasubedi",
    #     "act": "adrian.uribe",
    #     "aesthetic_nursing": "manancosmetolog",
    #     "game": "jynxziwrohu",
    #     "social": "lifeofharrison",
    #     "clothing": "erika.dwyer",
    #     "car": "gfyleec",
    #     "food": "janelleandkate",
    #     "animal": "knucklebumpfarms",
    #     "family": "valeji",
    #     "drama": "5minutosdehistoria",
    #     "fitness": "trainingtall",
    #     "education": "fluentjoy_english",
    #     "technology": "crismxrtinez",
    # }
    #
    # category_list = list(big_v.keys())
    #
    # print()
    #
    # for category in category_list:
    #
    #     generate_sampled_follower_id_list(category, 200, 2024)
    # generate_sampled_followee_user_id_list('gioandrade_oficial','comedy')
