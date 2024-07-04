"""
@author: Lobster
@software: PyCharm
@file: crawler.py
@time: 2024/2/26 9:12
@description: main file for crawling tiktok data
"""
import os
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import json
from utils import convert_date, compare_dates, make_logger
from bs4 import BeautifulSoup


def init_browser(path):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_extension(r'D:\MicroVideoDatasetBuilder\ublock.crx')
    browser = webdriver.Chrome(path, chrome_options=options)
    return browser


def crawl_video_info_through_user_id(user_id_list, init_date, save_path='/checkpoints/video/tiktok'):
    logger.info("Author: Lobster")
    current_list = [x[:-5] for x in os.listdir(save_path)]
    user_id_list = list(set(user_id_list) - set(current_list))
    tiktok_website_url = r'https://www.tiktok.com/explore'
    browser = init_browser('../chromedriver.exe')
    browser.get(tiktok_website_url)
    try:
        button_visitors = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1cp64nz-DivTextContainer')))
        button_visitors[4].click()
    except Exception as e:
        logger.error(f"Error: {e}")
    for user_id in user_id_list:
        logger.info("-----------------------------------------------------------------------------------")
        logger.info(f"Start crawling user {user_id}")
        time.sleep(3)
        # 首先获取用户信息
        user_info_base_path = fr'D:\MicroVideoDatasetBuilder\Tiktok\user_info\{category}'
        user_info_path = os.path.join(user_info_base_path, f'{user_id}.json')
        personal_page_url = f'https://www.tiktok.com/@{user_id}'
        # 这个 try except 语句用于捕获异常，以捕获其他各种错误，如果该id无法爬取，就跳过它，例如它没有视频或者怎么样，就跳过它
        try:
            browser.get(personal_page_url)
            try:
                button_visitors = WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1cp64nz-DivTextContainer')))
                button_visitors[4].click()
            except Exception as e:
                pass
            time.sleep(2)
            try:
                nick_name = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'css-10pb43i-H2ShareSubTitle')))
                nick_name = nick_name.text
            except:
                with open(user_info_path, 'w', encoding='utf-8') as json_file:
                    json.dump("", json_file, ensure_ascii=False, indent=4)
                logger.info(f"User {user_id} does not exist now, skip it!")  # juliasnascc
                continue
            try:
                follow_info = WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-mgke3u-DivNumber')))
            except:
                with open(user_info_path, 'w', encoding='utf-8') as json_file:
                    json.dump("", json_file, ensure_ascii=False, indent=4)
                logger.info(f"User {user_id} is a secret account, skip it!")
                continue
            followee = follow_info[0].text.split('\n')
            followee = followee[0]
            follower = follow_info[1].text.split('\n')
            follower = follower[0]
            total_likes = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'css-ntsum2-DivNumber')))
            total_likes = total_likes.text.split('\n')
            total_likes = total_likes[0]
            desc = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'css-4ac4gk-H2ShareDesc')))
            desc = desc.text
            user_info = {
                'user_id': user_id,
                'nickname': nick_name,
                'personal_page_url': personal_page_url,
                'followee': followee,
                'follower': follower,
                'total_likes': total_likes,
                'desc': desc
            }
            with open(user_info_path, 'w', encoding='utf-8') as json_file:
                json.dump(user_info, json_file, ensure_ascii=False, indent=4)
            # 开始获取视频信息
            try:
                video_cover = WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-x6y88p-DivItemContainerV2')))
                video_cover[0].click()

            except:
                logger.info(f"User {user_id} has no video, skip it !")
                continue
            time.sleep(1)
            # number_of_videos = 30
            current_number_of_videos = 0
            while True:
                time.sleep(1)
                try:
                    if current_number_of_videos != 0:
                        # try except 语句用于捕获异常，以确保最后一个视频之后不再点击下一个视频按钮
                        try:
                            next_video_button = WebDriverWait(browser, 10).until(
                                EC.element_to_be_clickable(
                                    (By.CLASS_NAME, 'css-1s9jpf8-ButtonBasicButtonContainer-StyledVideoSwitch')))
                            time.sleep(1)
                            next_video_button.click()
                        except:
                            logger.info(f"Finish crawling user {user_id}")
                            break
                    # 视频基本信息抓取区域
                    # 获取视频链接
                    video_url = browser.current_url
                    file_name = generate_video_info_file_name(video_url)
                    if os.path.exists(fr'D:\MicroVideoDatasetBuilder\Tiktok\video_info\{category}\{file_name}'):
                        logger.info(f"Video {video_url} has been crawled, skip it!")
                        current_number_of_videos += 1
                        time.sleep(3)
                        continue
                    # 获取视频标题, try except 语句用于捕获异常，以防止视频无标题的情况
                    try:
                        video_title = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'css-1wdx3tj-DivContainer')))
                        video_title = video_title.text
                    except:
                        video_title = ''
                    # 获取视频的基本信息
                    # 这里不直接用selenium的原因是，
                    # 作者在实践时发现，当时间是几x前的时候，selenium有概率会获取不到时间，因此直接通过selenium先返回页面源码，然后再用BeautifulSoup来解析出视频基本信息
                    soup = BeautifulSoup(browser.page_source, 'html.parser')
                    # 找到所有带有data-e2e="browser-nickname"属性的<span>标签
                    span_tags = soup.find_all('span', {'data-e2e': 'browser-nickname'})
                    # 遍历每个<span>标签，提取其内部文本
                    for span in span_tags:
                        # 查找所有直接子节点的文本内容，并以列表形式返回
                        text_contents = [child.text.strip() for child in span.find_all(recursive=False)]
                    upper_name = text_contents[0]
                    uploading_time = text_contents[2]
                    if uploading_time.count('-') != 2:
                        uploading_time = date_convert(uploading_time)
                    if compare_dates(uploading_time, init_date) == -1:
                        current_number_of_videos += 1
                        if current_number_of_videos <= 3:
                            time.sleep(3)
                            continue
                        else:
                            logger.info(f"Finish crawling user {user_id}")
                            time.sleep(1)
                            break
                    # 获取视频的点赞、评论和分享数
                    statics_info = WebDriverWait(browser, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, 'e1hk3hf92')))
                    likes = statics_info[0].text
                    comments = statics_info[1].text
                    favorites = statics_info[2].text
                    # 筛查评论数是否过多，过多时，跳过这个视频
                    if 'K' in comments or 'M' in comments:
                        current_number_of_videos += 1
                        logger.info(f"Comments are too many, skip video: {video_url}")
                        time.sleep(2)
                        continue
                    elif int(comments) > 1500:
                        current_number_of_videos += 1
                        logger.info(f"Comments are too many, skip video: {video_url}")
                        time.sleep(2)
                        continue
                    # 定义保存数据的格式
                    file_path = os.path.join(fr'D:\MicroVideoDatasetBuilder\Tiktok\video_info\{category}', file_name)
                    video_info = {
                        "crawl_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "video_url": video_url,
                        "video_title": video_title,
                        "user_id": user_id,
                        "nickname": upper_name,
                        "uploading_time": uploading_time,
                        "likes": likes,
                        "comments": comments,
                        "favorites": favorites,
                        "comment": []  # 初始化评论列表
                    }
                    time.sleep(1)
                    # comment 数据抓取区域
                    # 使用 try except 语句来捕获异常，以防止无评论情况
                    try:
                        comment_container = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-xm2h10-PCommentText')))
                        # 将鼠标移动到评论区域
                        ActionChains(browser).move_to_element(comment_container[len(comment_container) - 1]).perform()
                        # 模拟下滑操作, 由于网站使用了分页加载，所以需要下滑几次来拉取更多的评论
                        scroll_times = 0
                        old_comment_list_length = len(comment_container)
                        while True:
                            if len(comment_container) < 5:
                                time.sleep(2)
                                break
                            # 在评论区域内按下 Page Down 键
                            ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
                            comment_container = WebDriverWait(browser, 10).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-xm2h10-PCommentText')))
                            ActionChains(browser).move_to_element(
                                comment_container[len(comment_container) - 1]).perform()
                            scroll_times += 1
                            # 通过判断comment的数量是否变化，来判断是否已经拉取到了所有的评论，模4是为了容错
                            if scroll_times % 4 == 0:
                                if len(comment_container) == old_comment_list_length:
                                    time.sleep(2)
                                    break
                                else:
                                    old_comment_list_length = len(comment_container)
                            time.sleep(2)
                        # 拿到评论的所有信息
                        comment_likes_element = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-gb2mrc-SpanCount')))
                        comment_username_element = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1665s4c-SpanUserNameText')))
                        comment_time_element = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-4tru0g-SpanCreatedTime')))
                        comment_user_url_element = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.CLASS_NAME, 'css-fx1avz-StyledLink-StyledUserLinkName')))
                        comment_text_element = WebDriverWait(browser, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-xm2h10-PCommentText')))
                        # 遍历评论信息，将其存储到字典中
                        for i in range(len(comment_text_element)):
                            comment_level = comment_text_element[i].get_attribute("data-e2e")
                            comment_text = comment_text_element[i].text
                            nick_name = comment_username_element[i].text
                            comment_time = comment_time_element[i].text
                            comment_user_url = comment_user_url_element[i].get_attribute('href')
                            comment_likes = comment_likes_element[i].text
                            comment = {
                                "comment_level": comment_level,
                                "comment_time": comment_time,
                                "comment_text": comment_text,
                                "comment_likes": comment_likes,
                                "user_id": comment_user_url.split('@')[-1],
                                "nickname": nick_name,
                                "personal_page_url": comment_user_url
                            }
                            video_info["comment"].append(comment)
                    except:
                        video_info["comment"] = []
                    with open(file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(video_info, json_file, ensure_ascii=False, indent=4)
                        logger.info(f"Finish crawling video: {video_url}")
                    current_number_of_videos += 1
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Video {video_url} has an error: {e}")
                    time.sleep(2)
                    continue
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(2)
            continue
    logger.info(f"Finish crawling {category} !")
    time.sleep(200)


def download_video_files(path, tiktok_download_website_url, category):
    logger = make_download_logger(category)
    logger.info(f"Start downloading {category} !")
    video_url_list = generate_video_url_list(category)
    small_sleep = 1
    big_sleep = 2
    browser = init_browser(path)
    browser.get('https://www.baidu.com')
    time.sleep(3)
    # browser.get(tiktok_download_website_url)
    # time.sleep(/big_sleep)
    browser.get(tiktok_download_website_url)
    for video_url in video_url_list:
        try:
            time.sleep(big_sleep)
            # 等待输入框可见
            url_input_box = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'url')))
            # 输入第一个视频链接
            url_input_box.send_keys(video_url)
            # 点击下载按钮
            go_to_download_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'button-go')))
            go_to_download_button.click()
            time.sleep(big_sleep)
            # except:
            #
            #     time.sleep(2)
            #
            #     logger.info(f"Video {video_url} has an error and can not be downloaded!")
            #
            #     print(1)
            #
            #     continue
            # try:
            #     close_button = WebDriverWait(browser, 2).until(EC.element_to_be_clickable((By.CLASS_NAME, 'modal-close')))
            #
            #     close_button.click()
            #
            # except:
            #
            #     pass  # 如果找不到广告关闭按钮，就跳过
            # time.sleep(10)
            # 等待下载按钮可见
            try:
                download_button = WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'download-file')))
                download_button.click()
            except:
                time.sleep(2)
                url_input_box.clear()
                logger.info(f"Video {video_url} has an error and can not be downloaded!")
                os.remove(
                    fr'D:\MicroVideoDatasetBuilder\Tiktok\video_info\{category}\{generate_video_info_file_name(video_url)}')
                continue
            try:
                close_button = WebDriverWait(browser, 2).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'modal-close')))
                close_button.click()
            except:
                pass  # 如果找不到广告关闭按钮，就跳过
            # 返回
            try:
                back_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'is-black')))
                back_button.click()
            except:
                continue
        except:
            browser.close()
            browser = init_browser(path)
            browser.get('https://www.baidu.com')
            time.sleep(3)
            browser.get(tiktok_download_website_url)
            video_url_list.append(video_url)
            continue
    # 最后等待所有视频下载完成
    time.sleep(200)


def crawl_followee_follower_id_list(user_id, category):
    browser = init_browser('../chromedriver.exe')
    # 这120s是为了手动登录，选择Google账户登录是最简单的方式
    browser.get(r'https://www.tiktok.com/explore')
    time.sleep(120)
    browser.get(fr'https://www.tiktok.com/@{user_id}')
    # 首先爬取关注的用户id
    # 点击关注按钮，弹出关注列表
    followee_button = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-mgke3u-DivNumber')))
    followee_button[0].click()
    # 不断滚动关注列表，拉取所有关注的用户id
    followee_id_container = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
    # 将鼠标移动到评论区域
    ActionChains(browser).move_to_element(followee_id_container[len(followee_id_container) - 1]).perform()
    # 模拟下滑操作, 由于网站使用了分页加载，所以需要下滑几次来拉取更多的评论
    scroll_times = 0
    old_followee_list_length = len(followee_id_container)
    while True:
        # 在评论区域内按下 Page Down 键
        ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
        followee_id_container = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
        ActionChains(browser).move_to_element(followee_id_container[len(followee_id_container) - 1]).perform()
        scroll_times += 1
        # 通过判断comment的数量是否变化，来判断是否已经拉取到了所有的评论，模4是为了容错
        if scroll_times % 4 == 0:
            if len(followee_id_container) == old_followee_list_length:
                time.sleep(2)
                break
            else:
                old_followee_list_length = len(followee_id_container)
        time.sleep(2)
    followee_id_list = []
    for i in range(len(followee_id_container)):
        followee_id_list.append(followee_id_container[i].text)
    time.sleep(2)
    # 接下来爬取粉丝的用户id
    # 点击粉丝按钮，弹出粉丝列表
    follower_button = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1oop42z-DivTabItem')))
    follower_button[0].click()
    # 不断滚动粉丝列表，拉取所有粉丝的用户id
    follower_id_container = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
    # 将鼠标移动到评论区域
    ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
    # 模拟下滑操作, 由于网站使用了分页加载，所以需要下滑几次来拉取更多的评论
    scroll_times = 0
    old_follower_list_length = len(follower_id_container)
    while True:
        # 在评论区域内按下 Page Down 键
        ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
        follower_id_container = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
        ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
        scroll_times += 1
        # 通过判断comment的数量是否变化，来判断是否已经拉取到了所有的评论，模4是为了容错
        if scroll_times % 4 == 0:
            if len(follower_id_container) == old_follower_list_length:
                time.sleep(2)
                break
            else:
                old_follower_list_length = len(follower_id_container)
        time.sleep(3)
    follower_id_list = []
    for i in range(len(follower_id_container)):
        follower_id_list.append(follower_id_container[i].text)
    follow_info = {
        'user_id': user_id,
        'followee': followee_id_list,
        'follower': follower_id_list
    }
    file_path = fr'D:\MicroVideoDatasetBuilder\Tiktok\follow_info\{category}\{user_id}.json'
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(follow_info, json_file, ensure_ascii=False, indent=4)


def crawl_follower_id_list(user_id, category):
    browser = init_browser('../chromedriver.exe')
    user_id_list = generate_sampled_followee_user_id_list(user_id, category)
    # 这120s是为了手动登录，选择Google账户登录是最简单的方式
    browser.get(r'https://www.tiktok.com/explore')
    time.sleep(120)
    for user_id in user_id_list:
        browser.get(fr'https://www.tiktok.com/@{user_id}')
        # 首先爬取关注的用户id
        # 点击关注按钮，弹出关注列表
        followee_button = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-mgke3u-DivNumber')))
        followee_button[0].click()
        time.sleep(2)
        # 接下来爬取粉丝的用户id
        # 点击粉丝按钮，弹出粉丝列表
        follower_button = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1oop42z-DivTabItem')))
        follower_button[0].click()
        # 不断滚动粉丝列表，拉取所有粉丝的用户id
        follower_id_container = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
        # 将鼠标移动到评论区域
        ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
        # 模拟下滑操作, 由于网站使用了分页加载，所以需要下滑几次来拉取更多的评论
        scroll_times = 0
        old_follower_list_length = len(follower_id_container)
        while True:
            # 在评论区域内按下 Page Down 键
            ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
            follower_id_container = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
            ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
            scroll_times += 1
            # 通过判断comment的数量是否变化，来判断是否已经拉取到了所有的评论，模4是为了容错
            if scroll_times % 4 == 0:
                if len(follower_id_container) == old_follower_list_length:
                    time.sleep(2)
                    break
                else:
                    old_follower_list_length = len(follower_id_container)
            time.sleep(3)
        follower_id_list = []
        for i in range(len(follower_id_container)):
            follower_id_list.append(follower_id_container[i].text)
        follow_info = {
            'user_id': user_id,
            'follower': follower_id_list
        }
        file_path = fr'D:\MicroVideoDatasetBuilder\Tiktok\follow_info\{category}\{user_id}.json'
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(follow_info, json_file, ensure_ascii=False, indent=4)


# def crawl_follower_id_list(user_id=1, category=1):
#
#     category_dict = {
#         "aesthetic_nursing": "manancosmetolog",
#         "sports": "haessik",
#         "anime_manga": "vidztoker",
#         "social": "lifeofharrison",
#         "car": "juicedgarage",
#         "food": "janelleandkate",
#         "animal": "knucklebumpfarms",
#         "fitness": "trainingtall",
#     }
#
#     browser = init_browser('../chromedriver.exe')
#
#     # 这120s是为了手动登录，选择Google账户登录是最简单的方式
#
#     browser.get(r'https://www.tiktok.com/explore')
#
#     time.sleep(120)
#
#     for i in range(0,1):
#
#         time.sleep(2)
#
#         category = 'others'
#
#         user_id = list(category_dict.values())[i]
#
#         user_id_list = ['thehoopgenius']
#
#         for user_id in user_id_list:
#
#             browser.get(fr'https://www.tiktok.com/@{user_id}')
#
#             # 首先爬取关注的用户id
#
#             # 点击关注按钮，弹出关注列表
#
#             try:
#
#                 followee_button = WebDriverWait(browser, 10).until(
#                     EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-mgke3u-DivNumber')))
#             except:
#                 print(f"{user_id} is a secret id")
#                 continue
#
#             followee_button[0].click()
#
#             time.sleep(2)
#
#             # 接下来爬取粉丝的用户id
#
#             # 点击粉丝按钮，弹出粉丝列表
#
#             follower_button = WebDriverWait(browser, 10).until(
#                 EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1oop42z-DivTabItem')))
#
#             follower_button[0].click()
#
#             # 不断滚动粉丝列表，拉取所有粉丝的用户id
#
#             follower_id_container = WebDriverWait(browser, 10).until(
#                 EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
#
#             # 将鼠标移动到评论区域
#
#             ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
#
#             # 模拟下滑操作, 由于网站使用了分页加载，所以需要下滑几次来拉取更多的评论
#
#             scroll_times = 0
#
#             old_follower_list_length = len(follower_id_container)
#
#             while True:
#
#                 # 在评论区域内按下 Page Down 键
#
#                 ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
#
#                 follower_id_container = WebDriverWait(browser, 10).until(
#                     EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
#
#                 ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
#
#                 scroll_times += 1
#
#                 # 通过判断comment的数量是否变化，来判断是否已经拉取到了所有的评论，模4是为了容错
#
#                 if scroll_times % 4 == 0:
#
#                     if len(follower_id_container) == old_follower_list_length:
#
#                         time.sleep(2)
#
#                         break
#                     else:
#
#                         old_follower_list_length = len(follower_id_container)
#
#                 time.sleep(3)
#
#             follower_id_list = []
#
#             for i in range(len(follower_id_container)):
#                 follower_id_list.append(follower_id_container[i].text)
#
#             follow_info = {
#                 'user_id': user_id,
#                 'follower': follower_id_list
#             }
#
#             file_path = fr'D:\MicroVideoDatasetBuilder\Tiktok\follow_info\{category}\{user_id}.json'
#
#             with open(file_path, 'w', encoding='utf-8') as json_file:
#
#                 json.dump(follow_info, json_file, ensure_ascii=False, indent=4)

def crawl_single_follower_id_list(user_id, category):
    browser = init_browser('../chromedriver.exe')
    # user_id_list = generate_followee_user_id_list(user_id, category)
    # 这120s是为了手动登录，选择Google账户登录是最简单的方式
    browser.get(r'https://www.tiktok.com/explore')
    time.sleep(120)
    browser.get(fr'https://www.tiktok.com/@{user_id}')
    # 首先爬取关注的用户id
    # 点击关注按钮，弹出关注列表
    followee_button = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-mgke3u-DivNumber')))
    followee_button[0].click()
    time.sleep(2)
    # 接下来爬取粉丝的用户id
    # 点击粉丝按钮，弹出粉丝列表
    follower_button = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1oop42z-DivTabItem')))
    follower_button[0].click()
    # 不断滚动粉丝列表，拉取所有粉丝的用户id
    follower_id_container = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
    # 将鼠标移动到评论区域
    ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
    # 模拟下滑操作, 由于网站使用了分页加载，所以需要下滑几次来拉取更多的评论
    scroll_times = 0
    old_follower_list_length = len(follower_id_container)
    while True:
        # 在评论区域内按下 Page Down 键
        ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
        follower_id_container = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-swczgi-PUniqueId')))
        ActionChains(browser).move_to_element(follower_id_container[len(follower_id_container) - 1]).perform()
        scroll_times += 1
        # 通过判断comment的数量是否变化，来判断是否已经拉取到了所有的评论，模4是为了容错
        if scroll_times % 4 == 0:
            if len(follower_id_container) == old_follower_list_length:
                time.sleep(2)
                break
            else:
                old_follower_list_length = len(follower_id_container)
        time.sleep(2)
    follower_id_list = []
    for i in range(len(follower_id_container)):
        follower_id_list.append(follower_id_container[i].text)
    follow_info = {
        'user_id': user_id,
        'follower': follower_id_list
    }
    file_path = fr'D:\MicroVideoDatasetBuilder\Tiktok\follow_info\{category}\{user_id}.json'
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(follow_info, json_file, ensure_ascii=False, indent=4)


def crawl_video_info_through_keywords(keywords):
    init_date = "2024-1-1"
    logger = make_logger(keywords)
    logger.info(f"Start crawling {keywords} !")
    logger.info("Author: Lobster")
    tiktok_website_url = r'https://www.tiktok.com/explore'
    browser = init_browser('D:\MicroVideoDatasetBuilder\chromedriver.exe')
    browser.get(tiktok_website_url)
    try:
        button_visitors = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1cp64nz-DivTextContainer')))
        button_visitors[4].click()
    except Exception as e:
        logger.error(f"Error: {e}")
    # css-1c7urt-SpanUniqueId userid
    input_box = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'css-1yf5w3n-InputElement')))
    time.sleep(2)
    input_box.send_keys(keywords)
    time.sleep(2)
    search_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'css-16dy42q-ButtonSearch')))
    search_button.click()
    time.sleep(80)
    video_cover = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1wa52dp-DivPlayerContainer')))
    video_cover[0].click()
    time.sleep(2)
    while True:
        user_id = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'css-1c7urt-SpanUniqueId')))
        user_id = user_id.text
        # user_info_base_path = fr'D:\MicroVideoDatasetBuilder\Tiktok\dataset_v2\user_info'
        #
        # user_info_path = os.path.join(user_info_base_path, f'{user_id}.json')
        personal_page_url = f'https://www.tiktok.com/@{user_id}'
        video_url = browser.current_url
        file_name = generate_video_info_file_name(video_url)
        # 检查当前视频是否已经爬取过
        if os.path.exists(fr'D:\MicroVideoDatasetBuilder\Tiktok\dataset_v2\video_info\{file_name}'):
            logger.info(f"Video {video_url} has been crawled, skip it!")
            time.sleep(3)
            try:
                next_video_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'css-1s9jpf8-ButtonBasicButtonContainer-StyledVideoSwitch')))
                time.sleep(1)
                next_video_button.click()
            except:
                logger.info(f"Finish crawling {keywords}")
                break
        try:
            video_title = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'css-1wdx3tj-DivContainer')))
            video_title = video_title.text
        except:
            video_title = ''
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        # 找到所有带有data-e2e="browser-nickname"属性的<span>标签
        span_tags = soup.find_all('span', {'data-e2e': 'browser-nickname'})
        # 遍历每个<span>标签，提取其内部文本
        for span in span_tags:
            # 查找所有直接子节点的文本内容，并以列表形式返回
            text_contents = [child.text.strip() for child in span.find_all(recursive=False)]
        upper_name = text_contents[0]
        uploading_time = text_contents[2]
        if uploading_time.count('-') != 2:
            uploading_time = date_convert(uploading_time)
        # 获取视频的点赞、评论和分享数
        statics_info = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'e1hk3hf92')))
        likes = statics_info[0].text
        comments = statics_info[1].text
        favorites = statics_info[2].text
        # 筛查评论数是否过多，过多时，跳过这个视频
        if 'K' in comments or 'M' in comments:
            logger.info(f"Comments are too many, skip video: {video_url}")
            time.sleep(2)
            try:
                next_video_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'css-1s9jpf8-ButtonBasicButtonContainer-StyledVideoSwitch')))
                time.sleep(1)
                next_video_button.click()
            except:
                logger.info(f"Finish crawling {keywords}")
                break
        elif int(comments) > 9999:
            logger.info(f"Comments are too many, skip video: {video_url}")
            time.sleep(2)
            try:
                next_video_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'css-1s9jpf8-ButtonBasicButtonContainer-StyledVideoSwitch')))
                time.sleep(1)
                next_video_button.click()
            except:
                logger.info(f"Finish crawling {keywords}")
                break
        # 定义保存数据的格式
        file_path = os.path.join(fr'D:\MicroVideoDatasetBuilder\Tiktok\dataset_v2\video_info', file_name)
        video_info = {
            "crawl_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "video_url": video_url,
            "video_title": video_title,
            "user_id": user_id,
            "nickname": upper_name,
            "uploading_time": uploading_time,
            "likes": likes,
            "comments": comments,
            "favorites": favorites,
            "comment": []  # 初始化评论列表
        }
        time.sleep(1)
        # comment 数据抓取区域
        # 使用 try except 语句来捕获异常，以防止无评论情况
        try:
            comment_container = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-xm2h10-PCommentText')))
            # TODO： 二级评论需要设计一下
            # reply_comment_button = WebDriverWait(browser, 10).until(
            #     EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-16xv7y2-PReplyActionText')))
            #
            # for i in range(len(reply_comment_button)):
            #     reply_comment_button[i].click()
            # 将鼠标移动到评论区域
            ActionChains(browser).move_to_element(comment_container[len(comment_container) - 1]).perform()
            # 模拟下滑操作, 由于网站使用了分页加载，所以需要下滑几次来拉取更多的评论
            scroll_times = 0
            old_comment_list_length = len(comment_container)
            while True:
                if len(comment_container) < 5:
                    time.sleep(2)
                    break
                # 在评论区域内按下 Page Down 键
                ActionChains(browser).send_keys(Keys.PAGE_DOWN).perform()
                comment_container = WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-xm2h10-PCommentText')))
                ActionChains(browser).move_to_element(comment_container[len(comment_container) - 1]).perform()
                # 二级评论要好好设计一下
                # reply_comment_button = WebDriverWait(browser, 10).until(
                #     EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-16xv7y2-PReplyActionText')))
                #
                # for i in range(len(reply_comment_button)):
                #     reply_comment_button[i].click()
                scroll_times += 1
                # 通过判断comment的数量是否变化，来判断是否已经拉取到了所有的评论，模4是为了容错
                if scroll_times % 4 == 0:
                    if len(comment_container) == old_comment_list_length:
                        time.sleep(2)
                        break
                    else:
                        old_comment_list_length = len(comment_container)
                time.sleep(2)
            # 拿到评论的所有信息
            comment_likes_element = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-gb2mrc-SpanCount')))
            comment_username_element = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1665s4c-SpanUserNameText')))
            comment_time_element = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-4tru0g-SpanCreatedTime')))
            comment_user_url_element = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'css-fx1avz-StyledLink-StyledUserLinkName')))
            comment_text_element = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-xm2h10-PCommentText')))
            # 遍历评论信息，将其存储到字典中
            for i in range(len(comment_text_element)):
                comment_level = comment_text_element[i].get_attribute("data-e2e")
                comment_text = comment_text_element[i].text
                nick_name = comment_username_element[i].text
                comment_time = comment_time_element[i].text
                comment_user_url = comment_user_url_element[i].get_attribute('href')
                comment_likes = comment_likes_element[i].text
                comment = {
                    "comment_level": comment_level,
                    "comment_time": comment_time,
                    "comment_text": comment_text,
                    "comment_likes": comment_likes,
                    "user_id": comment_user_url.split('@')[-1],
                    "nickname": nick_name,
                    "personal_page_url": comment_user_url
                }
                video_info["comment"].append(comment)
        except:
            video_info["comment"] = []
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(video_info, json_file, ensure_ascii=False, indent=4)
            logger.info(f"Finish crawling video: {video_url}")
        try:
            next_video_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'css-1s9jpf8-ButtonBasicButtonContainer-StyledVideoSwitch')))
            time.sleep(1)
            next_video_button.click()
        except:
            logger.info(f"Finish crawling {keywords}")
            break
    # logger.info("-----------------------------------------------------------------------------------")


if __name__ == '__main__':
    # crawl_video_info_through_user_id('education', "small")
    # download_video_files('../chromedriver.exe', r'https://snaptik.app/', 'technology')
    # download_video_files('../chromedriver.exe', r'https://snaptik.app/', 'social')
    # crawl_user_info_through_user_id('act')
    crawl_video_info_through_keywords('tiktok to be taken down')
