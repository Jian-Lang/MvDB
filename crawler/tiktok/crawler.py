# -*- coding: utf-8 -*-
# @Time    : 2024/2/26 9:12
# @Author  : jian lang
# @File    : crawler.py
# @Description: main file for crawling tiktok data

import os
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
from .utils import convert_date, compare_dates,init_browser, make_logger, check_dirs_exist,solve_popup
from bs4 import BeautifulSoup
from .parsers import build_parser


class TiktokCrawler:
    def __init__(self):
        self.user_id_list = json.load(open('config/tiktok/user_id.json', 'r'))

    def crawl_video_info_through_user_id(self):

        # 设置全局变量，用于判断是否已经弹出验证窗口，若已经弹出，则不再需要解决弹窗问题
        is_popup = False
        parser = build_parser('video_info')
        args = parser.parse_args()
        init_date = args.init_date
        max_comments = args.max_comments
        save_path = args.save_path

        user_id_list = self.user_id_list

        video_info_save_path = os.path.join(save_path,'video_info/tiktok')
        user_info_save_path = os.path.join(save_path, 'user_info/tiktok')
        check_dirs_exist(save_path)
        check_dirs_exist(video_info_save_path)
        check_dirs_exist(user_info_save_path)

        logger = make_logger(save_path)
        logger.info("Start crawling Tiktok video information!")

        current_list = [x[:-5] for x in os.listdir(user_info_save_path)]
        user_id_list = list(set(user_id_list) - set(current_list))
        tiktok_website_url = r'https://www.tiktok.com/explore'
        browser = init_browser('crawler/tools/chromedriver.exe')
        browser.get(tiktok_website_url)

        # 用于解决弹窗验证访客
        try:
            solve_popup(browser)
            is_popup = True
        except Exception as e:
            pass

        for user_id in user_id_list:
            logger.info(f"Start crawling user {user_id}")
            time.sleep(3)
            # 首先获取用户信息
            user_info_path = os.path.join(user_info_save_path, f'{user_id}.json')
            personal_page_url = f'https://www.tiktok.com/@{user_id}'
            # 这个 try except 语句用于捕获异常，以捕获其他各种错误，如果该id无法爬取，就跳过它，例如它没有视频或者怎么样，就跳过它
            try:
                browser.get(personal_page_url)

                # 若弹窗未解决，则尝试解决弹窗
                if not is_popup:
                    try:
                        solve_popup(browser)
                        is_popup = True
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

                    # 若弹窗未解决，则尝试解决弹窗
                    if not is_popup:
                        try:
                            solve_popup(browser)
                            is_popup = True
                        except Exception as e:
                            pass

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

                                # 若弹窗未解决，则尝试解决弹窗
                                if not is_popup:
                                    try:
                                        solve_popup(browser)
                                        is_popup = True
                                    except Exception as e:
                                        pass

                            except:
                                logger.info(f"Finish crawling user {user_id}")
                                break
                        # 视频基本信息抓取区域
                        # 获取视频链接
                        video_url = browser.current_url
                        video_id = video_url.replace('//','/').split('/')[-1]
                        video_info_path = os.path.join(video_info_save_path, f'{video_id}.json')

                        if os.path.exists(video_info_path):
                            logger.info(f"Video {video_id} has been crawled, skip it!")
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
                            uploading_time = convert_date(uploading_time)
                        if compare_dates(uploading_time, init_date) == -1:
                            logger.info(f"video {video_id} was published on {uploading_time} which is earlier than {init_date}, skip it!")
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
                            logger.info(f"Comments are too many, skip video: {video_id}")
                            time.sleep(2)
                            continue
                        elif int(comments) > max_comments:
                            current_number_of_videos += 1
                            logger.info(f"Comments are too many, skip video: {video_id}")
                            time.sleep(2)
                            continue
                        # 定义视频信息的数据结构
                        video_info = {
                            "crawl_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            "video_url": video_url,
                            "video_title": video_title,
                            "user_id": user_id,
                            "video_id": video_id,
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
                        with open(video_info_path, 'w', encoding='utf-8') as json_file:
                            json.dump(video_info, json_file, ensure_ascii=False, indent=4)
                            logger.info(f"Finish crawling video: {video_id}")
                        current_number_of_videos += 1
                        time.sleep(1)
                    except Exception as e:
                        logger.error(f"Video {video_id} has an error: {e}")
                        time.sleep(2)
                        continue
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(2)
                continue
        logger.info(f"Finish crawling!")
        time.sleep(200)


    def crawl_video_info_through_keywords(self,keywords):
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

if __name__ == '__main__':
    crawler = TiktokCrawler()
    crawler.crawl_video_info_through_user_id()
