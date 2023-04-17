#! /usr/bin/env python3
'''
'''
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ActionChains

import requests
import time
from enum import Enum

from WebClientException import LoginFailedException, InvalidStationNameException

class WebClient:
    '''
    member
    - _driver: chrome driver
    - _url_main
    '''
    def __init__(self, ui_on = False):
        '''
        webdriver 초기화
        '''
        options = webdriver.ChromeOptions()
        if not ui_on:
            options.add_argument('headless')
        self._driver = webdriver.Chrome(options=options)
        self._url_main = 'https://etk.srail.kr/main.do'
        self._url_login = 'https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000'


    ################### encapsulate webdriver ###################
    def _find_element_by_css_selector(self, css_selector):
        '''
        encapsulate WebDriver.find_element
        Return a DOM element.
        '''
        return self._driver.find_element(By.CSS_SELECTOR, css_selector)
    

    def _find_elements_by_css_selector(self, css_selector):
        '''
        encapsulate WebDriver.find_element
        Return multiple elements.
        '''
        return self._driver.find_elements(By.CSS_SELECTOR, css_selector)
    

    def _wait_for_element(self, timeout, css_selector):
        '''
        encapsulate WebDriverWait.
        return desired dom element.
        Dom element를 찾지 못하면 프로그램 종료.
        '''
        try:
            WebDriverWait(self._driver, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))
        except (TimeoutException, NoSuchElementException):
            print(f'\033[0;31m[Error] cannot find element like \'{css_selector}\'\033[0;37m')
            exit()

        return self._find_element_by_css_selector(css_selector)


    #############################################################
    

    def login(self, member_id, password):
        '''
        member_id - 회원 번호
        password - 비밀 번호
        raise LoginFailedException
        '''
        self._driver.get(self._url_login)
        self._wait_for_element(1, 'div.fl_l')
        self._find_element_by_css_selector('input[type="text"]#srchDvNm01').send_keys(member_id)
        self._find_element_by_css_selector('input[type="password"]').send_keys(password)
        try:
            self._find_element_by_css_selector('input[type="submit"]').click()
            self._wait_for_element(1, 'div#wrap')
        except UnexpectedAlertPresentException as alert:
            raise LoginFailedException(alert.alert_text)
        print('로그인 성공')


    def select_station(self, station_dpt, station_arv):
        '''
        departure - 출발역 이름
        arrival - 도착역 이름
        raise NoSuchElementException
        '''
        dropdown_dpt = self._find_element_by_css_selector('select#dptRsStnCd')
        dropdown_arv = self._find_element_by_css_selector('select#arvRsStnCd')
        valid_station_names = dropdown_arv.find_elements(By.CSS_SELECTOR, 'option')
        valid_station_names = [name.text for name in valid_station_names][1:]

        options_dpt = Select(dropdown_dpt)
        options_arv = Select(dropdown_arv)
        try: 
            options_dpt.select_by_visible_text(station_dpt)
            options_arv.select_by_visible_text(station_arv)
        except NoSuchElementException:
            print("유효한 기차역 이름==========")
            for name in valid_station_names:
                print(name)
            exit()

        print('[출발역 선택] %s' %(options_dpt.all_selected_options[0].text))
        print('[도착역 선택] %s' %(options_arv.all_selected_options[0].text))


    def select_date(self, month, date):
        '''
        month(str) - 월
        date(str) - 일
        month, date 모두 문자열 타입의 정수이고 유효한 값만 입력되었다고 가정한다.
        '''
        self._wait_for_element(1, 'input.calendar2').click()
        calendar_frame = self._wait_for_element(2, 'iframe#_LAYER_BODY_')
        # frame 전환 (default -> calendar) 
        self._driver.switch_to.frame(calendar_frame)
        months = self._driver.find_elements(By.CSS_SELECTOR, 'h2')
        months = [month.text[:-1] for month in months]
        # 이번 달
        target_month_css = 'div.this' 
        # 다음 달
        if month == months[1]:
            target_month_css = 'div.next'
        date_buttons = self._find_element_by_css_selector(target_month_css).find_elements(By.CSS_SELECTOR, 'a')
        for button in date_buttons:
            if button.text == date:
                self._wait_for_element(1, 'a')
                print(f'[날짜 선택] {button.text}')
                button.click()
                self._driver.switch_to.default_content
                break
        

    def select_time(self, time_min):
        '''
        time_min - 00, 01, 02, ... 22까지의 정수라고 가정한다.
        '''
        if int(time_min)%2 != 0:
            time_min = str(int(time_min)+1)
        dropdown_tm = self._find_element_by_css_selector('select#dptTm')
        options_tm = Select(dropdown_tm)
        time_min += '0000'
        options_tm.select_by_value(time_min)


    def select_passenger_number(self, adult, child):
        '''
        adult - 만 13세 이상
        child - 만 6세 ~ 만 12세
        모두 0부터 9까지 가능
        '''
        dropdown_adult = self._find_element_by_css_selector('select#psgInfoPerPrnb1')
        dropdown_child = self._find_element_by_css_selector('select#psgInfoPerPrnb5')
        Select(dropdown_adult).select_by_value(adult)
        Select(dropdown_child).select_by_value(child)
        print("[탑승자 구성] 어른 %s, 어린이 %s" %(adult, child))


    def quick_inquiry(self):
        '''
        간편 조회 클릭
        '''
        self._find_element_by_css_selector('a[onclick="selectScheduleList(); return false;"]').click()
        try:
            self._wait_for_element(5, 'tbody')
            # tbody = self._find_element_by_css_selector('tbody')
        except Exception: 
            print("남은 승차권이 없습니다.")


    def available_seat(self, row, is_executive):
        '''
        특실, 일반실 중 예약 가능한 좌석의 예약하기 버튼 element를 반환한다.
        '''
        data_regular = row.find_elements(By.CSS_SELECTOR, 'td')[6]
        data_executive = row.find_elements(By.CSS_SELECTOR, 'td')[5]
        if is_executive:
            for td in data_regular+data_executive:
                if len(td.find_elements(By.CSS_SELECTOR, 'a')) == 2:    # 예약 가능
                    return td.find_element(By.CSS_SELECTOR, 'a')        # 첫 번째 <a>가 예약하기 버튼이다.
        else:
            if len(data_regular.find_elements(By.CSS_SELECTOR, 'a')) == 2:    # 예약 가능
                return data_regular.find_element(By.CSS_SELECTOR, 'a')        # 첫 번째 <a>가 예약하기 버튼이다.
        return None


    def select_option(self, time_max, executive):
        '''
        executive - True이면 특실 우선, False이면 일반실 우선
        False인 경우 특실이 예약될 수는 없지만 True인 경우에는 일반실이 
        예약될 수 있다.
        좌석은 알아서 배정된다.
        '''
        table_rows = self._find_elements_by_css_selector('tr')[2:]
        print("승차권 탐색...")
        for tr in table_rows:
            tds = tr.find_elements(By.CSS_SELECTOR, 'td')
            train = tds[1].text
            dpt_stn, dpt_time_full = tds[3].find_element(By.CSS_SELECTOR, 'div').text, \
                    tds[3].find_element(By.CSS_SELECTOR, 'em.time').text
            '''tr
            |0   |1       |2       |3     |4     |5       |6       |7       |8        |9       |10      |11
            |구분|열차종류|열차번호|출발역|도착역|특실    |일반실  |예약대기|회원 할인|운행시간|운임요금|소요시간
            -----------------------------------------------------------------------------------------------------
            |직통|SRT     |370     |대전  |수서  |예약하기|예약하기|   -    |    -    |보기    |보기    |01:06
            |    |        |        |22:05 |23:11 |죄석선택|좌석선택|   -    |    -    |        |        |
            또는 
            |직통|SRT     |370     |대전  |수서  |좌석부족|예약하기|   -    |    -    |보기    |보기    |01:06
            |    |        |        |22:05 |23:11 |        |좌석선택|   -    |    -    |        |        |
            또는
            |직통|SRT     |370     |대전  |수서  |매진    |예약하기|   -    |    -    |보기    |보기    |01:06
            |    |        |        |22:05 |23:11 |        |좌석선택|   -    |    -    |        |        |
            '''
            dpt_time = tr.find_element(By.CSS_SELECTOR, 'em.time').text[:2]
            if int(dpt_time) < int(time_max) and self.available_seat(tr, executive) is not None:
                self.available_seat(tr, executive).click()
                print("\033[1;32m%s %s %s \033[1;37m" % (train, dpt_stn, dpt_time_full))
                return
            else:
                print("%s %s %s 매진/자리 없음" % (train, dpt_stn, dpt_time_full))
        else:
            print("매진")
            # exit()


    def settle(self):
        '''
        결제
        '''
        # TODO a.btn_large를 못 찾는 경우가 잦다
        self._wait_for_element(5, 'a.btn_large')
        self._find_element_by_css_selector('a.btn_large').click()
        self._wait_for_element(2, 'a#chTab2')
        self._find_element_by_css_selector('a#chTab2').click()
        self._wait_for_element(2, 'input#kakaoPay.checkbox')
        self._find_element_by_css_selector('input#kakaoPay.checkbox').click()
        self._wait_for_element(2, 'div.tab3')
        btns = self._find_element_by_css_selector('div.tab3').find_elements(By.CSS_SELECTOR, 'a')
        for btn in btns:
            if '스마트폰' in btn.text:
                btn.click()
        # handle alert popup
        WebDriverWait(self._driver, 2).until(EC.alert_is_present())
        self._driver.switch_to.alert.accept()
        self._driver.switch_to.default_content
        self._find_element_by_css_selector('a#requestIssue2').click()

    
    def send_kakaoPay_request(self, phone_number, birthday):
        kakaoPay_popup = self._driver.window_handles[1]
        self._driver.switch_to.window(kakaoPay_popup)
        self._wait_for_element(2, 'button.swiper-pagination-bullet')
        btns = self._find_elements_by_css_selector('button.swiper-pagination-bullet')
        for btn in btns:
            print(btn.text)
        # btns[1].send_keys(Keys.ENTER)
        btns[1].click()
        phone_field = self._find_element_by_css_selector('input#userPhone')
        birthday_field = self._find_element_by_css_selector('input#userBirth')
        # uninteractable element에 javascript를 사용하여 값 입력
        self._driver.execute_script("arguments[0].value=arguments[1];", phone_field, phone_number)
        time.sleep(3)
        self._driver.execute_script("arguments[0].value=arguments[1];", birthday_field, birthday)
        form_user_post = self._find_element_by_css_selector('form#userPost')
        form_user_post.submit()


################### dev ###################

    def print_cookies(self):
        print()
        print("cookies=====================================")
        cookies = self._driver.get_cookies()
        for cookie in cookies:
            for k, v in cookie.items():
                print('%-10s: %-32s' % (k,v))
        print()

######### reservation info #########
MEMBER_ID = <srt 회원번호>           
MEMBER_PW = <srt 비밀번호>    
DEPT_STATION = '대전'              
ARV_STATION = '수서'               
TIME_MIN = '10'                    
TIME_MAX = '22'                    
MONTH = '4'                        
DATE = '7'                        
NUM_OF_ADULT = '2'                 
NUM_OF_CHILD = '0'                 
SRT_ONLY = True                    
EXECUTIVE = False                  
USER_PHONE_NUMBER = <카카오페이 전화번호> 
USER_BIRTHDAY = <카카오페이 생일>
####################################
####################################
    

def dont_exit_until():
    key_in = 'a'
    while key_in != 'exit':
        key_in = input()
    print("GoodBye")

start_time = time.time()
ui_option = True
browser = WebClient(ui_option)
try:
    browser.login(MEMBER_ID, MEMBER_PW)
except LoginFailedException as e:
    print(e)
    exit()
browser.select_station(DEPT_STATION, ARV_STATION)
browser.select_date(MONTH, DATE)
browser.select_time(TIME_MIN)
browser.select_passenger_number(NUM_OF_ADULT, NUM_OF_CHILD)
# TODO 특정 차표에 대해 일정 횟수 이상 검색하면 리다이렉션된다.
browser.quick_inquiry()
browser.select_option(TIME_MAX, EXECUTIVE)
browser.settle()
browser.send_kakaoPay_request(USER_PHONE_NUMBER, USER_BIRTHDAY)

print("elapsed time: %0.2fs" %(time.time()-start_time))

if ui_option:
    dont_exit_until()
###########################################
