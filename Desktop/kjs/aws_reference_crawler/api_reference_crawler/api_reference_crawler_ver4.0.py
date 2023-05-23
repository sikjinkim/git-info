from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re
import datetime
import pandas as pd
import logging

from sqlalchemy import create_engine

from urllib.request import urlopen
from bs4 import BeautifulSoup

class apiReferenceCrawler :

    api_reference_xpath_dict = {
        "english_button": "/html/body/div[2]/div/div/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div[3]/div[2]/div/div/div/ul/li[3]/div[1]/div/span/span/span/span",
        "language_button": "/html/body/div[2]/div/div/div[1]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div[1]/button",
        "category_list": "/html/body/div/div/div/div/main/div/div/div/div/section/div/div/div/div/div/div/ul/li/a",
        "service_list": "/html/body/div[2]/div/div/div[2]/main/div[2]/div/div[2]/div/section[2]/div[2]/div[2]/div/div/div[2]/div/ol/li/div/div/div/div/div/h5/a",
        "service_section_title": "/html/body/div/div/div/div/div/div/div/main/div/div/div/div/div/section/div/div/div/div/ol/li/div/div/div/h3/a",
        "service_section_contents": "/html/body/div/div/div/div/div/div/div/main/div/div/div/div/div/section/div/div/div/div/ol/li/div/div/div/div/div",
        "side_contents": "/html/body/div/div/div/div/div/div/div/div/div/nav/div/div/div/ul/li/div/div/a"
    }

    def __init__(
        self,
        main_url = "https://docs.aws.amazon.com/index.html",
        executable_path="/home/drex/ast_ai/siksik/timeseries_anomalies_detection/aws_reference_crawler/chromedriver",
        api_columns_list=["crawling_time_utc", "unique_key", "aws_category", "aws_service", "api_aws_service", "api_event_name",
                            "description_eng", "tokenized_description_eng", "len_tokenized_description_eng", "chk_sum_description_eng", "description_kor", 
                            "api_url", "api_html", "tokenized_api_html", "len_tokenized_api_html", "chk_sum_api_html",
                            "last_unique_key", "changed_col", "changed_cont", "version", "gpt_html_summary", "gpt_changed_cont"]
    ) :
        self.main_url = main_url
        self.executable_path = executable_path
        self.api_columns_list = api_columns_list
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(executable_path=self.executable_path, options=self.chrome_options)
        self.driver.implicitly_wait(30)  # 한번 설정하면 모든 코드에 적용, 설정한 시간보다 일찍 완료되면 다음 코드 수행
        self.wait = WebDriverWait(self.driver, 60)  # 조건이 성립하지 않으면 timeout으로 설정된 시간만큼 최대한 기다림
        self.scroll_actions = ActionChains(self.driver)

    # 언어 선택 함수
    def choose_language(self, language_xpath: str, english_xpath: str):
        # 언어선택 선언 및 클릭
        language_button = self.driver.find_element(By.XPATH, self.api_reference_xpath_dict[language_xpath])
        language_button.click()

        # English 선택
        english_button = self.driver.find_element(By.XPATH, self.api_reference_xpath_dict[english_xpath])
        self.scroll_actions.move_to_element(english_button).perform()
        time.sleep(0.2)

        english_button.click()
        print("English 선택 완료")
        time.sleep(0.5)

    # windows 개수 1로 하는 함수
    def make_one_window(self):
        # 열려있는 window의 갯수
        len_windows = len(self.driver.window_handles)

        # 열려있는 window의 갯수가 1보다 클 경우
        while len_windows > 1:
            # 마지막에 열린 window로 이동
            self.driver.switch_to.window(self.driver.window_handles[-1])
            # 윈도우 종료
            self.driver.close()
            time.sleep(0.5)

            # window가 1이 될때까지 진행
            len_windows -= 1

        self.driver.switch_to.window(self.driver.window_handles[0])

    # dataframe 생성 함수
    def make_dataframe(self, data_value: list, columns_value: list):
        if data_value == None:
            columns = columns_value
            dataframe = pd.DataFrame(columns=columns)
        else:
            data = [data_value]
            columns = columns_value
            dataframe = pd.DataFrame(data=data, columns=columns)

        return dataframe

    # scroll 이동 후 click 하는 함수
    def move_scroll_and_click(self, element, click_method: str):
        # element로 스크롤 이동
        self.scroll_actions.move_to_element(element).perform()
        time.sleep(0.2)

        # click_method가 'click'일 경우 -> 그냥 클릭
        if click_method == "click":
            self.wait.until(EC.element_to_be_clickable(element))
            element.click()
            time.sleep(0.4)

        # click_method가 'ctrl_click'일 경우 -> ctrl + 클릭
        if click_method == "ctrl_click":
            self.wait.until(EC.element_to_be_clickable(element))
            element.send_keys(Keys.CONTROL + "\n")
            time.sleep(0.4)

    # n번째 탭으로 이동하는 함수
    def switch_windows(self, nth_window: int):
        # nth_window번째 탭으로 이동
        self.driver.switch_to.window(self.driver.window_handles[nth_window])
        time.sleep(0.4)


    def crawling_reference_data(self, index, aws_category, api_reference_table, aws_service_element) :

        # aws_service 선언
        aws_service = aws_service_element.text

        # aws_service가 "AWS", "Amazon"으로 시작하는 경우
        if aws_service_element.text.startswith("AWS ") or aws_service_element.text.startswith("Amazon ") :
            aws_service = " ".join(aws_service_element.text.split(" ")[1:])
        print("# ======= aws_service:", aws_service)

        # service_element로 스크롤 이동 후 'ctrl + click'하고 1번탭으로 driver 이동
        self.move_scroll_and_click(element= aws_service_element, click_method= 'ctrl_click')
        self.switch_windows(1)

        try :
            # 서비스 접속 시 section의 title, contents
            service_section_title_list = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.api_reference_xpath_dict["service_section_title"])))
            service_section_title_list = [section_title if section_title != None else None for section_title in service_section_title_list]

            service_section_contents_list = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.api_reference_xpath_dict["service_section_contents"])))
            service_section_contents_list = [section_contents if section_contents != None else None for section_contents in service_section_contents_list]

            # title, contents list를 하나의 dict 형태로 변환
            service_section_dict = dict(zip(service_section_title_list, service_section_contents_list))

            for service_section in service_section_dict.items() :
                
                service_section_title_element = service_section[0]
                service_section_contents_element = service_section[1]

                # service_section_title에 "api reference"가 있고 "sdk" 혹은 "java"가 없는 경우 OR service_section_contents에 "api reference"가 있고 service
                if ("api reference" in service_section_title_element.text.lower() or "api reference" in service_section_contents_element.text.lower()) and ("sdk" or "java") not in service_section_title_element.text.lower() :
                    print("# --- api reference type :", service_section_title_element.text)

                    # service_section_title_element로 스크롤 이동 후 'ctrl_click' 후 2번탭으로 driver 이동
                    self.move_scroll_and_click(element= service_section_title_element, click_method= 'ctrl_click')
                    self.switch_windows(2)

                    # section_title_element click 후에 있는 side contents
                    side_contents_list = self.driver.find_elements(By.XPATH, self.api_reference_xpath_dict['side_contents'])
                    for side_contents_element in side_contents_list :

                        # Actions 찾기
                        if side_contents_element.text == 'Actions' :
                            print('actions 있음')
                            actions_element = side_contents_element

                            # actions_element로 스크롤 이동 후 'ctrl_click'하고 3번탭으로 driver 이동
                            self.move_scroll_and_click(element= actions_element, click_method= 'ctrl_click')
                            self.switch_windows(3)

                            event_name_list = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div/main/div/div/div[1]/div/div/div[3]/div[1]/div/ul/li/p/a")
                            for event_name_element in event_name_list :
                                    
                                # api_event_name
                                api_event_name = event_name_element.text
                                print("# api_event_name :", api_event_name)

                                self.move_scroll_and_click(element= event_name_element, click_method= 'ctrl_click')
                                self.switch_windows(4)

                                # crawling_time 선언
                                crawlingtime_element = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                                crawling_time = datetime.datetime.strptime(crawlingtime_element, "%Y-%m-%d %H:%M:%S")
                                print("# crawling_time :", crawling_time)

                                # unique_key 선언
                                unique_key = ("".join(((str(crawling_time)).split(" ")[0]).split("-")) + "_" + str(index))
                                print("# unique_key :", unique_key)

                                # api_url 선언
                                api_url = str(self.driver.current_url)
                                print("# api_url :", api_url)

                                # api_aws_service 선언
                                api_aws_service = api_url.split("/")[3]
                                print("# api_aws_service :", api_aws_service)

                                # description_eng 선언
                                try:
                                    description_eng = (self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main-col-body > p")))).text
                                    if (description_eng == "" or description_eng == " ") :
                                        description_eng = None

                                    else:
                                        description_eng = description_eng

                                except:
                                    description_eng = None
                                print("# description_eng :", description_eng)

                                # api_html 선언
                                api_html = str(BeautifulSoup(urlopen(self.driver.current_url), "html.parser"))
                                print("# api_html : crawlnig...\n")

                                line_api_reference_table = self.make_dataframe(
                                    data_value= [crawling_time, unique_key, aws_category, aws_service, api_aws_service, api_event_name,
                                                description_eng, None, None, None, None,
                                                api_url, api_html, None, None, None,
                                                None, None, None, None, None, None],
                                    columns_value= self.api_columns_list
                                )

                                api_reference_table = pd.concat([api_reference_table, line_api_reference_table], axis= 0)

                                index += 1

                                self.driver.close()
                                time.sleep(0.2)
                                self.switch_windows(3)

                            self.driver.close()
                            time.sleep(0.2)
                            self.switch_windows(2)

                            break

                        elif ("api reference" in side_contents_element.text.lower()) or (("aws" and "api") in side_contents_element.text.lower()) :
                            print("###### action말고 다른거 :", side_contents_element.text)

                            # content_element로 스크롤 이동 후 'click'
                            self.move_scroll_and_click(element= side_contents_element, click_method= 'click')

                            # actions 있는 경우
                            try :
                                actions_element = self.driver.find_element(By.LINK_TEXT, 'Actions')

                                # actions_element로 스크롤 이동 후 'ctrl_click' 후 3번탭으로 driver 이동
                                self.move_scroll_and_click(element= actions_element, click_method= 'ctrl_click')
                                self.switch_windows(3)

                                event_name_list = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div/main/div/div/div[1]/div/div/div[3]/div[1]/div/ul/li/p/a")
                                for event_name_element in event_name_list :
                                        
                                    # api_event_name
                                    api_event_name = event_name_element.text
                                    print("# api_event_name :", api_event_name)

                                    self.move_scroll_and_click(element= event_name_element, click_method= 'ctrl_click')
                                    self.switch_windows(4)

                                    # crawling_time 선언
                                    crawlingtime_element = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                                    crawling_time = datetime.datetime.strptime(crawlingtime_element, "%Y-%m-%d %H:%M:%S")
                                    print("# crawling_time :", crawling_time)

                                    # unique_key 선언
                                    unique_key = ("".join(((str(crawling_time)).split(" ")[0]).split("-")) + "_" + str(index))
                                    print("# unique_key :", unique_key)

                                    # api_url 선언
                                    api_url = str(self.driver.current_url)
                                    print("# api_url :", api_url)

                                    # api_aws_service 선언
                                    api_aws_service = api_url.split("/")[3]
                                    print("# api_aws_service :", api_aws_service)

                                    # description_eng 선언
                                    try:
                                        description_eng = (self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main-col-body > p")))).text
                                        if (description_eng == "" or description_eng == " ") :
                                            description_eng = None

                                        else:
                                            description_eng = description_eng

                                    except:
                                        description_eng = None
                                    print("# description_eng :", description_eng)

                                    # api_html 선언
                                    api_html = str(BeautifulSoup(urlopen(self.driver.current_url), "html.parser"))
                                    print("# api_html : crawlnig...\n")

                                    line_api_reference_table = self.make_dataframe(
                                        data_value= [crawling_time, unique_key, aws_category, aws_service, api_aws_service, api_event_name,
                                                    description_eng, None, None, None, None,
                                                    api_url, api_html, None, None, None,
                                                    None, None, None, None, None, None],
                                        columns_value= self.api_columns_list
                                    )

                                    api_reference_table = pd.concat([api_reference_table, line_api_reference_table], axis= 0)

                                    index += 1

                                    self.driver.close()
                                    time.sleep(0.2)
                                    self.switch_windows(3)

                                self.driver.close()
                                time.sleep(0.2)
                                self.switch_windows(2)

                                break

                            # actions 없는 경우
                            except :
                                pass

                        else :
                            pass

                    self.driver.close()
                    time.sleep(0.2)
                    self.switch_windows(1)

        except :
            pass

        self.driver.close()
        time.sleep(0.2)
        self.switch_windows(0)


    def crawling_api_reference(self) :
        # 언어선택 함수 실행
        self.choose_language(language_xpath="language_button", english_xpath="english_button")

        # index
        index = 0

        # aws_category_list
        aws_category_list = self.driver.find_elements(By.XPATH, self.api_reference_xpath_dict['category_list'])
        for category_element in aws_category_list :
            
            # aws category 선언
            aws_category = category_element.text
            # aws_category가 "All products"인 경우
            if aws_category == 'All products' :
                pass

            # aws_category가 "All products"가 아닌 나머지의 경우
            else :
                print("\n# ======= aws_category:", aws_category, "======= #")
                self.move_scroll_and_click(element= category_element, click_method= 'click')

                api_reference_table = self.make_dataframe(
                    data_value= None,
                    columns_value= self.api_columns_list
                )

                # category 선택 시 service pagination
                pagination_button_list = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[2]/main/div[2]/div/div[2]/div/section[2]/div[2]/div[2]/div/div/div[1]/div/div[2]/div[2]/div/ul/li/button")

                # service pagination의 길이가 3인경우 -> pagination 없음
                if len(pagination_button_list) == 3:
                    # aws_service_list
                    aws_service_element_list = self.driver.find_elements(By.XPATH, self.api_reference_xpath_dict['service_list'])
                    for aws_service_element in aws_service_element_list :
                        self.crawling_reference_data(index, aws_category, api_reference_table, aws_service_element)

                    # 필요없는 탭 닫기
                    self.make_one_window()

                    # 메인페이지로 이동
                    self.driver.get(url=self.main_url)
                    time.sleep(0.5)
                    
                # service pagination의 길이가 4 이상인 경우 -> pagination 있음
                elif len(pagination_button_list) >= 4 :
                    page_list = pagination_button_list[1:len(pagination_button_list)-1]
                    
                    for page_num in page_list :
                        self.move_scroll_and_click(element= page_num, click_method= 'click')
                        # aws_service_list
                        aws_service_element_list = self.driver.find_elements(By.XPATH, self.api_reference_xpath_dict['service_list'])
                        for aws_service_element in aws_service_element_list :
                            self.crawling_reference_data(index, aws_category, api_reference_table, aws_service_element)

                    # 필요없는 탭 닫기
                    self.make_one_window()

                    # 메인페이지로 이동
                    self.driver.get(url=self.main_url)
                    time.sleep(0.5)

                # dataframe 적재
                if len(api_reference_table) == 0:
                    print("적재 안됨\n")
                    pass
                else:
                    self.insert_into_db(api_reference_table, "new_api_reference_table_v4")
                    print("적재 완료\n")

api_reference_crawler = apiReferenceCrawler()

driver = api_reference_crawler.driver
driver.get(api_reference_crawler.main_url)

api_reference_crawler.crawling_api_reference()