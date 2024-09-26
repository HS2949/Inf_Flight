# config.py
import config

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText

from datetime import datetime
import time
import requests
import json
import re

import xmltodict

def click_continue():
    """continue 버튼 클릭 (쿠키 메시지 처리)"""
    try:
        continue_button = WebDriverWait(config.driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Continue"]'))
        )
        continue_button.click()
        # 팝업이 닫힐 시간을 대기
        time.sleep(1)
    except Exception as e:
        print(f"Error clicking the continue button")


def send_kakao_message(text):
    """KakaoTalk 메시지 보내기"""
    with open(r"D:\kakao_code.json", "r") as fp:
        tokens = json.load(fp)

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {"Authorization": "Bearer " + tokens["access_token"]}

    data = {
        "template_object": json.dumps(
            {"object_type": "text", "text": text, "link": {"web_url": "www.naver.com"}}
        )
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    if response.json().get("result_code") == 0:
        print("메시지를 성공적으로 보냈습니다.")
    else:
        print(
            "메시지를 성공적으로 보내지 못했습니다. 오류메시지 : "
            + str(response.json())
        )


def send_email(full_message, sender_email, sender_password, receiver_email):
    """Gmail 보내기"""
    # 메일 제목 설정

    # SMTP 서버 설정 및 로그인
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, sender_password)

    # 메일 내용 설정
    msg = MIMEText(full_message)
    msg["Subject"] = config.subject

    # 메일 보내기
    smtp.sendmail(sender_email, receiver_email, msg.as_string())

    # SMTP 객체 닫기
    smtp.quit()

    print(f"\n\n메일을 성공적으로 보냈습니다. {receiver_email} \n {config.subject}\n")


def get_disruptions_text():
    """distuption 텍스트 가져오기"""
    try:
        disruptions_element = WebDriverWait(config.driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".disruptions-carousel"))
        )
        return disruptions_element.text
    except Exception as e:
        print(f"Error fetching disruptions information")
        return ""


def pagination_work():
    """(초기) 공항 혼잡도 및 정보 가져오기 (페이지네이션)
    Returns:
        full_message: 초기에 공항 혼잡도 정보 넣기"""
    try:

        # 특정 요소에서 텍스트 가져오기 및 페이지네이션 처리
        disruptions_texts = []

        # 페이지네이션을 통해 모든 텍스트 수집
        collect_all_pagination_texts(disruptions_texts)

        # 텍스트 결과 편집하여 저장
        config.full_message += format_disruption_texts(disruptions_texts)

        # 주차장 정보 얻기
        config.full_message += get_airport_parking_data() + "\n\n\n"

    except Exception as e:
        print(f"Error navigating to the first page")


def go_to_first_page():
    """(초기) 첫 페이지 버튼 누르기"""
    try:
        # 첫 페이지 버튼 찾기
        first_page_button = config.driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='carousel__goto__1']"
        )

        # 'disabled' 상태가 아닌 경우에만 클릭
        if "disabled" not in first_page_button.get_attribute("class"):
            first_page_button.click()
            time.sleep(1)  # 페이지 이동 대기 시간
            # print("Navigated to the first page.")
        # else:
        # print("Already on the first page.")

    except Exception as e:
        print(f"Error navigating to the first page")


# 페이지네이션을 통해 모든 텍스트 수집
def collect_all_pagination_texts(disruptions_texts):
    """(초기) 페이지네이션 순차적으로 누르며 텍스트 가져오기"""
    try:
        # 페이지네이션 첫번째 페이지 클릭
        go_to_first_page()  # Ensure we start from the first page
        # 페이지네이션 순차적으로 클릭
        while True:
            # 텍스트 크롤링
            disruptions_text = get_disruptions_text()
            if disruptions_text:
                disruptions_texts.append(disruptions_text)

            # 다음 페이지 버튼을 찾기
            try:
                next_button = config.driver.find_element(
                    By.CSS_SELECTOR, "button[data-testid='carousel__nav__next']"
                )

                if "disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(1)  # 페이지가 로드될 시간을 대기
            except Exception as e:
                # print(f"Error clicking the next button: {e}")
                break
    except Exception as e:
        print(f"Error collect_all_pagination_texts")


def format_disruption_texts(texts):
    """(초기) 텍스트를 원하는 형식으로 변환하는 함수 (한글 번역)"""
    formatted_text = "" #"\n" + "=" * 50 + "\n"
    # 처리할 순서 정의 (3, 2, 1, 4 순서)
    order = [2, 1, 0, 3]

    # 지정된 순서에 따라 반복
    for idx in order:
        text = texts[idx]
        lines = text.split("\n")
        category = lines[0]
        formatted_text += f"\n{'-'*40}\n       {category}\n{'-'*40}\n" if idx == 2 else ""
        # 마지막 줄을 제외한 모든 줄을 반복
        for i in range(1, len(lines) - 1, 2):
            # 항목명 번역
            key_korean = (
                lines[i]
                .replace("FLIGHTS DELAYED", "지연 항공편")
                .replace("FLIGHTS CANCELED", "취소 항공편")
                .replace("AVERAGE DELAY", "평균 지연 시간")
                .replace("DISRUPTION INDEX", "혼잡도 지수")
            )

            key_korean = f"     ※ {key_korean} (어제) " if idx == 0 else f"     ※ {key_korean} (내일) "  if idx == 3 else f"☞ {key_korean:15}"
            formatted_text += f"        {key_korean} : {lines[i+1].replace("(","  (")}"
            if "DISRUPTION INDEX" in lines[i]:
                disruption_value = float(lines[i + 1])
                formatted_text += f"          ▶ "
                if 0 <= disruption_value <= 1.9:
                    formatted_text += f"양호한 교통 흐름"
                elif 2.0 <= disruption_value <= 3.4:
                    formatted_text += f"약간의 문제, 일부 지연 또는 취소"
                elif 3.5 <= disruption_value <= 5:
                    formatted_text += f"심각한 문제, 장기 지연 및 다수의 항공편 취소"
                formatted_text += f"\n\n"
            else:
                formatted_text += f"\n"

    # 구문 번역
    formatted_text = (
        formatted_text.replace("YESTERDAY", "어제")
        .replace("TODAY", "오늘")
        .replace("TOMORROW", "내일")
        .replace("FLIGHT DISRUPTIONS", "제주공항 운항 현황") #"항공편 운항 지연"
        .replace("CURRENT DISRUPTIONS", "현재 혼잡 상황")
    )

    # Full message에 공항 혼잡도 정보 넣기
    formatted_text += "=" * 35 

    return formatted_text.strip()


def fetch_flight_info(flight_number, passenger_number):
    """항공편 찾고 드랍박스 클릭 후 정보 크롤링 - 항공편 1개
    Returns:
        results : key에 대한 항공편 값을 저장
        all_Plain_results : 모든 항공편 값 저장
    """
    try:
        # 'flight_number' 텍스트를 포함하는 li 요소 찾기
        print(f"항공편 : {flight_number} 조회 중..")
        flight_li = WebDriverWait(config.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//li[contains(., "{flight_number}")]')
            )
        )
        # 해당 li 요소 내에서 드롭박스 버튼 찾기
        dropdown_button = flight_li.find_element(By.XPATH, './/button[@class="px-1"]')

        # JavaScript를 사용하여 포커스 설정
        config.driver.execute_script("arguments[0].focus();", dropdown_button)

        # 드롭박스 버튼 클릭
        dropdown_button.click()
        time.sleep(1)
        # print(f"Dropdown button for {flight_number} clicked successfully.")

        # 항공편 ID 가져오기
        flight_id = flight_li.get_attribute("id")

        # 결과 저장할 딕셔너리
        results = {}

        # 각 XPath에 대해 텍스트 값을 가져오기
        for key, xpath in config.xpaths_text.items():
            try:
                element = WebDriverWait(config.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, xpath.replace("항공편", flight_id))
                    )
                )
                if "N/A" in element.text:
                    results[key] = ""
                else:
                    results[key] = merge_lines(element.text.strip())

            except Exception as e:
                print(f"Error finding element for {key}")
                results[key] = "N/A"

        # all_Plain_resultsdml 전체 배열에 각 편의 정보(results) 저장
        results["flight_number"] = flight_number
        config.all_Plain_results.append(results)

        print(
            f"           성공 : {flight_number:10} -  {merge_lines(results['FROM']):<20}\n         {results['SCHEDULED DEPARTURE']} → {results['SCHEDULED ARRIVAL']}"
        )

        return results

    except Exception as e:
        # print(f"Error finding and clicking the dropdown button or collecting information for {flight_number}: {e}")
        # print(f"#에러 : {e}")
        return None  # f"\n{'Flight Number':20} : {flight_number:10} - {passenger_number} 명\n  No data found.\n"


def text_flight_info(flight_number, passenger_number, results):
    """항공편 정보를 text 변환
    Returns:
        result_str: 텍스트 한글 번역 후 크롤링한 정보
    """
    try:
        # 결과를 문자열로 저장
        result_str = (
            f"\n{'Flight Number':20} : {flight_number:10} - {passenger_number} 명\n"
        )

        # key에 따라 데이터 수정 및 조정
        for key in config.key_inf:
            if key in results:
                txt = ""
                if "ACTUAL DEPARTURE" == key:
                    # ACTUAL DEPARTURE에 시간 차이 추가
                    if (
                        results["SCHEDULED DEPARTURE"] != ""
                        and results["ACTUAL DEPARTURE"] != ""
                    ):
                        minutes_difference = calculate_time_difference(
                            "real",
                            extract_time_from_text(
                                "time", results["SCHEDULED DEPARTURE"]
                            ),
                            extract_time_from_text("time", results["ACTUAL DEPARTURE"]),
                        )
                        txt = f"({'+' if minutes_difference > 0 else ''}{minutes_difference} min)"
                if "STATUS" == key:
                    # STATUS 시간 차이 추가
                    if results["SCHEDULED ARRIVAL"] != "" and results["STATUS"] != "":
                        minutes_difference = calculate_time_difference(
                            "real",
                            extract_time_from_text(
                                "time", results["SCHEDULED ARRIVAL"]
                            ),
                            extract_time_from_text("time", results["STATUS"]),
                        )
                        txt = f"({'+' if minutes_difference > 0 else ''}{minutes_difference} min)" if minutes_difference != 0 else ""
                # result_str += f"{key:20} : {merge_lines(results[key]):<30} {txt} \n"   #영문
                result_str += f"{config.translations[key]} :".ljust(15) + f"{results[key]}".rjust(10) + f"{txt}".rjust(25) + f"\n" if results[key] != "" else ""  # 한글
        return result_str

    except Exception as e:
        # print(f"Error finding and clicking the dropdown button or collecting information for {flight_number}: {e}")
        # print(f"#에러 : text_flight_info")
        print(f"         No data found.\n")
        return f"\n{'Flight Number':20} : {flight_number:10} - {passenger_number} 명\n     No data found.\n"


def calculate_time_difference(type, time_str1, time_str2):
    """텍스트 형식의 두 시간 차이 계산

    Args:
        type : integer = 정수 (절대값)
               real, float = 실수 (양수, 음수)

        time_str1 (text): "10:06 AM"
        time_str2 (text): datetime.now().strftime('%I:%M %p')

    Returns:
        integer : 차이나는 분 숫자 리턴
    """
    try:
        # 두 개의 시간 문자열을 datetime 객체로 변환
        time_object1 = datetime.strptime(time_str1, "%I:%M %p")
        time_object2 = datetime.strptime(time_str2, "%I:%M %p")

        # 시간을 동일한 날짜로 맞추기 위해 현재 날짜 사용
        now = datetime.now()
        time_object1 = time_object1.replace(year=now.year, month=now.month, day=now.day)
        time_object2 = time_object2.replace(year=now.year, month=now.month, day=now.day)

        # 시간 차이를 분 단위로 계산
        time_difference = (time_object2 - time_object1).total_seconds() / 60

        return (
            abs(int(time_difference))
            if type.lower() == "integer"
            else int(time_difference)
        )
    except ValueError:
        # print(f"ValueError: Invalid time format for scheduled '{scheduled}' or actual '{actual}'")
        return 0
    except Exception as e:
        # print(f"Unexpected error in calculate_time_difference: {e}")
        return 0


def extract_time_from_text(type, text):
    """텍스트에서 "10:06 AM" 형식의 시간 또는 시간 외 텍스트 추출
    Args:
        type : text = 시간 외 텍스트 추출
               time = 시간 텍스트 추출 "10:06 AM"
    """
    try:
        if type == "time":
            # 정규 표현식으로 '시간:분 AM/PM' 형식의 시간 추출
            match = re.search(r"\b\d{1,2}:\d{2} [AP]M\b", text)
            if match:
                return match.group(0).strip()  # 일치하는 시간 반환
            return None  # 일치하는 시간이 없으면 None 반환
        else:
            # 시간 형식을 제외한 텍스트를 추출 (시간:분 AM/PM 형식을 제외한 텍스트)
            text_without_time = re.sub(r"\b\d{1,2}:\d{2} [AP]M\b", "", text)
            # 앞뒤에 남은 공백을 제거
            return text_without_time.strip()
    except Exception as e:
        # 에러가 발생할 경우 에러 메시지를 반환
        return f"An error occurred: {str(e)}"


def merge_lines(text):
    """여러 줄의 텍스트를 한 줄로 변경하는 함수"""
    # 각 줄을 합쳐서 한 줄로 만들기
    single_line_text = " ".join(text.splitlines())
    return single_line_text


def click_button(css_selector, wait_time=2):
    """css 정보로 버튼 클릭"""
    try:
        # 버튼이 클릭 가능해질 때까지 대기
        button = WebDriverWait(config.driver, wait_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        button.click()
        # 버튼 클릭 후 대기
        time.sleep(wait_time)
    except Exception as e:
        print(f"Error clicking the button with selector '{css_selector}'")


def prework_button_click():
    """현재 시간 전후의 비행정보 버튼 클릭"""

    # "Load earlier flights" 버튼 클릭
    click_button(
        'button[data-testid="airport-arrival-departure__load-earlier-flights"]'
    )

    # "Load later flights" 버튼 클릭
    click_button('button[data-testid="airport-arrival-departure__load-later-flights"]')




def get_airport_parking_data():
    """공항 주차장 정보 크롤링 API"""
    try:
        # API로부터 데이터 가져오기
        response = requests.get(config.parking_url)

        # XML 데이터를 JSON 형식으로 변환
        if response.status_code == 200:
            xml_data = response.content
            dict_data = xmltodict.parse(xml_data)
            json_data = json.dumps(dict_data, indent=4, ensure_ascii=False)

            # JSON 데이터 파싱
            data = json.loads(json_data)

            # 저장할 딕셔너리
            parking_data = {}

            # 각 항목을 처리
            for item in data["response"]["body"]["items"]["item"]:
                parking_name = item["parkingAirportCodeName"]
                parking_date = item["parkingGetdate"]
                parking_time = item["parkingGettime"]
                

                # parkingGetdate와 parkingGettime을 합쳐서 datetime 형식으로 저장
                get_time = datetime.strptime(f"{parking_date} {parking_time}", "%Y-%m-%d %H:%M:%S")

                # 딕셔너리에 저장할 데이터
                parking_data[parking_name] = {
                    "parkingFullSpace": item["parkingFullSpace"],
                    "parkingIincnt": item["parkingIincnt"],
                    "parkingIoutcnt": item["parkingIoutcnt"],
                    "parkingIstay": item["parkingIstay"],
                    "GetTime": get_time
                }


                            
            # 요일을 한글로 변환
            weekdays_kr = ['월', '화', '수', '목', '금', '토', '일'] # 한글 요일 리스트
            day_of_week = weekdays_kr[get_time.weekday()]
            formatted_time = get_time.strftime(f"%Y-%m-%d ({day_of_week}) %p %I:%M")
            text_output = f"\n        ☞ 주차장 현황  {formatted_time}\n"

            # 각 항목을 처리
            for item in data["response"]["body"]["items"]["item"]:
                parking_name = item["parkingAirportCodeName"]
                parking_full_space = int(item["parkingFullSpace"])
                parking_stay = int(item["parkingIstay"])  
                
                # 사용 비율 계산 (소수점 반올림하여 백분율로 표시)
                usage_percentage = round((parking_stay / parking_full_space) * 100)

                # 여유 공간 계산
                remaining_space = parking_full_space - parking_stay
                
                # 주차장 상태 문자열 작성
                text_output += f"             - {parking_name:<12} ({usage_percentage:>3}%)    여유 : ".rjust(30)
                text_output += f"{remaining_space:<7}({parking_stay:>4} / {parking_full_space:>4})".rjust(10) + f"\n"  # 현재 주차량과 총 공간을 우측에 맞춰 표시
                
            return text_output
        else:
            print(f"주차정보 에러 : {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"주차정보 에러 : {response.status_code}")
        return None

