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
        print(f"Error clicking the continue button: {e}")


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
    subject = f"제주공항 현황 : {config.current_time}"

    # SMTP 서버 설정 및 로그인
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, sender_password)

    # 메일 내용 설정
    msg = MIMEText(full_message)
    msg["Subject"] = subject

    # 메일 보내기
    smtp.sendmail(sender_email, receiver_email, msg.as_string())

    # SMTP 객체 닫기
    smtp.quit()

    print(f"\n\n메일을 성공적으로 보냈습니다. {receiver_email} \n {subject}")


def get_disruptions_text():
    """distuption 텍스트 가져오기"""
    try:
        disruptions_element = WebDriverWait(config.driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".disruptions-carousel"))
        )
        return disruptions_element.text
    except Exception as e:
        print(f"Error fetching disruptions information: {e}")
        return ""


def go_to_first_page():
    """(초기) 첫 페이지 버튼 누르기"""
    try:
        first_page_button = config.driver.find_element(
            By.CSS_SELECTOR, ".disruptions-carousel__prev"
        )
        while not "disabled" in first_page_button.get_attribute("class"):
            first_page_button.click()
            time.sleep(1)
            first_page_button = config.driver.find_element(
                By.CSS_SELECTOR, ".disruptions-carousel__prev"
            )
    except Exception as e:
        print(f"Error navigating to the first page: {e}")


# 페이지네이션을 통해 모든 텍스트 수집
def collect_all_pagination_texts(disruptions_texts):
    """(초기) 페이지네이션 순차적으로 누르며 텍스트 가져오기"""
    go_to_first_page()  # Ensure we start from the first page
    while True:
        disruptions_text = get_disruptions_text()
        if disruptions_text:
            disruptions_texts.append(disruptions_text)

        # 다음 페이지 버튼을 찾기
        try:
            next_button = config.driver.find_element(
                By.CSS_SELECTOR, ".disruptions-carousel__next"
            )
            if "disabled" in next_button.get_attribute("class"):
                break
            next_button.click()
            time.sleep(1)  # 페이지가 로드될 시간을 대기
        except Exception as e:
            print(f"Error clicking the next button: {e}")
            break

def format_disruption_texts(texts):
    """ (초기) 텍스트를 원하는 형식으로 변환하는 함수"""
    formatted_text = ""
    for text in texts:
        lines = text.split("\n")
        category = lines[0]
        formatted_text += f"\n\n{'-'*28}\n{category}\n{'-'*28}\n"
        # 마지막 줄을 제외한 모든 줄을 반복
        for i in range(1, len(lines) - 1, 2):
            formatted_text += f"     {lines[i]} : {lines[i+1]}\n"
            if "DISRUPTION INDEX" in lines[i]:
                disruption_value = float(lines[i + 1])
                if 0 <= disruption_value <= 1.9:
                    formatted_text += "          - Good traffic flow\n"
                elif 2.0 <= disruption_value <= 3.4:
                    formatted_text += "          - Minor problems with some delays or few cancellations\n"
                elif 3.5 <= disruption_value <= 5:
                    formatted_text += "          - Major problems with long delays and several canceled flights\n"

    return formatted_text.strip()



def fetch_flight_info(flight_number, passenger_number):
    """항공편 찾고 드랍박스 클릭 후 정보 크롤링 - 항공편 1개
    Returns:
        result_str: 텍스트 한글 번역 후 크롤링한 정보
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

        # 정보 수집을 위한 XPath 리스트
        #xpaths = config.xpaths_text().replace("항공편", flight_id)

        # 결과 저장할 딕셔너리
        results = {}

        # 각 XPath에 대해 텍스트 값을 가져오기
        for key, xpath in config.xpaths_text.items():
            try:
                element = WebDriverWait(config.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath.replace("항공편", flight_id)))
                )
                if "N/A" in element.text:
                    results[key] = ""
                else:
                    results[key] = element.text

            except Exception as e:
                print(f"Error finding element for {key}: {e}")
                results[key] = "N/A"

        print(
            f"           성공 : {flight_number:10} -  {merge_lines(results['FROM']):<20}\n         {results['SCHEDULED DEPARTURE']} → {results['SCHEDULED ARRIVAL']}"
        )

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
                        txt = calculate_time_difference(
                            results["SCHEDULED DEPARTURE"], results["ACTUAL DEPARTURE"]
                        )
                if "STATUS" == key:
                    # STATUS 시간 차이 추가
                    if results["SCHEDULED ARRIVAL"] != "" and results["STATUS"] != "":
                        txt = calculate_time_difference(
                            results["SCHEDULED ARRIVAL"], results["STATUS"]
                        )
                # result_str += f"{key:20} : {merge_lines(results[key]):<30} {txt} \n"   #영문
                result_str += f"{config.translations[key]:20} : {merge_lines(results[key]):<30} {txt} \n"  # 한글
        return result_str

    except Exception as e:
        # print(f"Error finding and clicking the dropdown button or collecting information for {flight_number}: {e}")
        print(f"#에러 : {e}")
        return f"\n{'Flight Number':20} : {flight_number:10} - {passenger_number} 명\nNo data found.\n"


def calculate_time_difference(scheduled, actual):
    """ 시간 차이 계산 함수"""
    try:
        # 공백 제거
        scheduled = scheduled.strip()
        actual = actual.strip()

        lines = actual.split("\n")
        scheduled_time = datetime.strptime(scheduled, "%I:%M %p")
        actual_time = datetime.strptime(lines[len(lines) - 1], "%I:%M %p")
        time_difference = actual_time - scheduled_time
        minutes_difference = int(time_difference.total_seconds() / 60)
        if minutes_difference > 0:
            txt = f"(+{minutes_difference} min)"
        else:
            txt = f"({minutes_difference} min)"
        return txt
    except ValueError:
        # print(f"ValueError: Invalid time format for scheduled '{scheduled}' or actual '{actual}'")
        return ""
    except Exception as e:
        # print(f"Unexpected error in calculate_time_difference: {e}")
        return ""


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
        print(f"Error clicking the button with selector '{css_selector}': {e}")


def prework_button_click():
    """현재 시간 전후의 비행정보 버튼 클릭"""

    # "Load earlier flights" 버튼 클릭
    click_button('button[data-testid="airport-arrival-departure__load-earlier-flights"]')

    # "Load later flights" 버튼 클릭
    click_button('button[data-testid="airport-arrival-departure__load-later-flights"]')

