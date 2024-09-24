from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import requests
import json
from selenium.webdriver.chrome.service import Service

# WebDriver 설정
#service = ChromeService(executable_path=ChromeDriverManager().install())
#driver = webdriver.Chrome(service=service)
driver_path = "D:/Py_code/chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Flightradar24에서 특정 공항의 도착 페이지 열기
url = 'https://www.flightradar24.com/airport/cju/arrivals'
driver.get(url)

# 페이지가 로드될 시간을 대기
time.sleep(2)

# "continue" 버튼 클릭 (쿠키 메시지 처리)
try:
    continue_button = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Continue"]'))
    )
    continue_button.click()
    # 팝업이 닫힐 시간을 대기
    time.sleep(1)
except Exception as e:
    print(f"Error clicking the continue button: {e}")





# KakaoTalk 메시지 보내기
def send_kakao_message(text):
    with open(r"D:\kakao_code.json","r") as fp:
        tokens = json.load(fp)

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Authorization": "Bearer " + tokens["access_token"]
    }

    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "www.naver.com"
            }
        })
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    if response.json().get('result_code') == 0:
        print('메시지를 성공적으로 보냈습니다.')
    else:
        print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(response.json()))


# Gmail 보내기
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
def send_email(full_message, sender_email, sender_password, receiver_email):
    # 현재 날짜와 시간 가져오기
    current_time = datetime.now().strftime('%Y-%m-%d(%a) %H:%M')

    # 메일 제목 설정
    subject = f"제주공항 현황 : {current_time}"

    # SMTP 서버 설정 및 로그인
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, sender_password)

    # 메일 내용 설정
    msg = MIMEText(full_message)
    msg['Subject'] = subject

    # 메일 보내기
    smtp.sendmail(sender_email, receiver_email, msg.as_string())

    # SMTP 객체 닫기
    smtp.quit()

    print (f"\n\n메일을 성공적으로 보냈습니다. {receiver_email} \n {subject}")




# 특정 요소에서 텍스트 가져오기 및 페이지네이션 처리
disruptions_texts = []

def get_disruptions_text():
    try:
        disruptions_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.disruptions-carousel'))
        )
        return disruptions_element.text
    except Exception as e:
        print(f"Error fetching disruptions information: {e}")
        return ""

def go_to_first_page():
    try:
        first_page_button = driver.find_element(By.CSS_SELECTOR, '.disruptions-carousel__prev')
        while not 'disabled' in first_page_button.get_attribute('class'):
            first_page_button.click()
            time.sleep(1)
            first_page_button = driver.find_element(By.CSS_SELECTOR, '.disruptions-carousel__prev')
    except Exception as e:
        print(f"Error navigating to the first page: {e}")

def collect_all_pagination_texts():
    go_to_first_page()  # Ensure we start from the first page
    while True:
        disruptions_text = get_disruptions_text()
        if disruptions_text:
            disruptions_texts.append(disruptions_text)

        # 다음 페이지 버튼을 찾기
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '.disruptions-carousel__next')
            if 'disabled' in next_button.get_attribute('class'):
                break
            next_button.click()
            time.sleep(1)  # 페이지가 로드될 시간을 대기
        except Exception as e:
            print(f"Error clicking the next button: {e}")
            break

# 페이지네이션을 통해 모든 텍스트 수집
collect_all_pagination_texts()

def fetch_flight_info(driver, flight_number, passenger_number):
    try:
        # 'flight_number' 텍스트를 포함하는 li 요소 찾기
        print(f"항공편 : {flight_number} 조회 중..")
        flight_li = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//li[contains(., "{flight_number}")]'))
        )
        # 해당 li 요소 내에서 드롭박스 버튼 찾기
        dropdown_button = flight_li.find_element(By.XPATH, './/button[@class="px-1"]')

        # JavaScript를 사용하여 포커스 설정
        driver.execute_script("arguments[0].focus();", dropdown_button)

        # 드롭박스 버튼 클릭
        dropdown_button.click()
        time.sleep(1)
        #print(f"Dropdown button for {flight_number} clicked successfully.")

        # 항공편 ID 가져오기
        flight_id = flight_li.get_attribute('id')

        # 정보 수집을 위한 XPath 리스트
        xpaths = {
            "FROM": f'//*[@id="{flight_id}"]/div[1]/div/div/div[3]/div[1]',
            "SCHEDULED DEPARTURE": f'//*[@id="{flight_id}"]/div[2]/div[1]/div/div[1]/div[2]',
            "ACTUAL DEPARTURE": f'//*[@id="{flight_id}"]/div[2]/div[1]/div/div[2]/div[2]',
            "SCHEDULED ARRIVAL": f'//*[@id="{flight_id}"]/div[2]/div[1]/div/div[3]/div[2]',
            "STATUS": f'//*[@id="{flight_id}"]/div[2]/div[1]/div/div[5]/div[2]',
            "GATE": f'//*[@id="{flight_id}"]/div[2]/div[3]/div[2]/div/div[2]',
            "BAGGAGE BELT": f'//*[@id="{flight_id}"]/div[2]/div[3]/div[3]/div/div[2]'
        }

        # 한글 번역 딕셔너리
        translations = {
            "FROM": "    항공 출발지",
            "SCHEDULED DEPARTURE": "예정 출발 시간",
            "ACTUAL DEPARTURE": "실제 출발 시간",
            "SCHEDULED ARRIVAL": "예정 도착 시간",
            "STATUS": "상태",
            "GATE": "게이트",
            "BAGGAGE BELT": "수하물 벨트"
        }

        # 결과 저장할 딕셔너리
        results = {}

        # 각 XPath에 대해 텍스트 값을 가져오기
        for key, xpath in xpaths.items():
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if "N/A" in element.text:
                    results[key] = ""
                else:
                    results[key] = element.text
                    
            except Exception as e:
                print(f"Error finding element for {key}: {e}")
                results[key] = "N/A"


        print(f"           성공 : {flight_number:10} -  {merge_lines(results['FROM']):<20}\n         {results['SCHEDULED DEPARTURE']} → {results['SCHEDULED ARRIVAL']}")

        # 결과를 문자열로 저장
        result_str = f"\n{'Flight Number':20} : {flight_number:10} - {passenger_number} 명\n"
        for key in ["FROM", "SCHEDULED DEPARTURE", "ACTUAL DEPARTURE", "SCHEDULED ARRIVAL", "STATUS", "GATE", "BAGGAGE BELT"]:
            if key in results:
                txt = ""
                if "ACTUAL DEPARTURE" == key:
                    # ACTUAL DEPARTURE에 시간 차이 추가
                    if results["SCHEDULED DEPARTURE"] != "" and results["ACTUAL DEPARTURE"] != "":
                        txt = calculate_time_difference(results["SCHEDULED DEPARTURE"], results["ACTUAL DEPARTURE"])
                if "STATUS" == key:
                    # STATUS 시간 차이 추가
                    if results["SCHEDULED ARRIVAL"] != "" and results["STATUS"] != "":
                        txt = calculate_time_difference(results["SCHEDULED ARRIVAL"], results["STATUS"])
                # result_str += f"{key:20} : {merge_lines(results[key]):<30} {txt} \n"   #영문
                result_str += f"{translations[key]:20} : {merge_lines(results[key]):<30} {txt} \n"   #한글
        return result_str

    except Exception as e:
        #print(f"Error finding and clicking the dropdown button or collecting information for {flight_number}: {e}")
        print(f"#에러 : {e}")
        return f"\n{'Flight Number':20} : {flight_number:10} - {passenger_number} 명\nNo data found.\n"


# 시간 차이 계산 함수
import datetime
def calculate_time_difference(scheduled, actual):
    try:
        # 공백 제거
        scheduled = scheduled.strip()
        actual = actual.strip()

        lines = actual.split("\n")
        scheduled_time = datetime.datetime.strptime(scheduled, '%I:%M %p')
        actual_time = datetime.datetime.strptime(lines[len(lines)-1], '%I:%M %p')
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


# 여러 줄의 텍스트를 한 줄로 변경하는 함수
def merge_lines(text):
    # 각 줄을 합쳐서 한 줄로 만들기
    single_line_text = ' '.join(text.splitlines())
    return single_line_text

# 텍스트를 원하는 형식으로 변환하는 함수
def format_disruption_texts(texts):
    formatted_text = ""
    for text in texts:
        lines = text.split("\n")
        category = lines[0]
        formatted_text += f"\n\n{'-'*28}\n{category}\n{'-'*28}\n"
        # 마지막 줄을 제외한 모든 줄을 반복
        for i in range(1, len(lines) - 1, 2):
            formatted_text += f"     {lines[i]} : {lines[i+1]}\n"
            if "DISRUPTION INDEX" in lines[i]:
                disruption_value = float(lines[i+1])
                if 0 <= disruption_value <= 1.9:
                    formatted_text += "          - Good traffic flow\n"
                elif 2.0 <= disruption_value <= 3.4:
                    formatted_text += "          - Minor problems with some delays or few cancellations\n"
                elif 3.5 <= disruption_value <= 5:
                    formatted_text += "          - Major problems with long delays and several canceled flights\n"

    return formatted_text.strip()

# 비행 전후 버튼 클릭
def prework_button_click():

    # "Load earlier flights" 버튼 클릭
    try:
        load_earlier_flights_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="airport-arrival-departure__load-earlier-flights"]'))
        )
        load_earlier_flights_button.click()
        # 버튼 클릭 후 대기 시간
        time.sleep(2)
    except Exception as e:
        print(f"Error clicking the load earlier flights button: {e}")


    # "Load later flights" 버튼 클릭
    try:
        load_later_flights_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="airport-arrival-departure__load-later-flights"]'))
        )
        load_later_flights_button.click()
        # 버튼 클릭 후 대기 시간
        time.sleep(2)
    except Exception as e:
        print(f"Error clicking the load later flights button: {e}")


# 실행할 항공편 번호 목록
flight_numbers = ['KE1055', 'KE1515', 'KE1607', 'KE1709', 'OZ8941', 'KE1569', 'BX8183']
passenger_numbers = ['1호차 - 8', '1호차 - 3', '2', '3', '16', '1', '4']


# 비행 전후 버튼 클릭
prework_button_click()

# 각 항공편 번호에 대해 정보 가져오기
all_results = ""
for i in range(0, len(flight_numbers) , 1) :
    cleaned_flight_number = flight_numbers[i].strip().upper()
    all_results += fetch_flight_info(driver, cleaned_flight_number, passenger_numbers[i])


# 드라이버 종료
driver.quit()

# # 수집한 텍스트 출력
# print( "\n\n\n제주공항 현황\n" + "="*48 )
# formatted_disruptions = format_disruption_texts(disruptions_texts)
# print(formatted_disruptions)

# # 항공편 결과 출력
# print("="*50 + "\n")
# print(all_results)

# 전체 메세지 내용
from datetime import datetime
current_time = datetime.now().strftime('%Y-%m-%d(%a) %H:%M')
full_message = f"\n\n제주공항 현황 : {current_time}\n" + "="*50 + "\n"
formatted_disruptions = format_disruption_texts(disruptions_texts)
full_message += formatted_disruptions + "\n"
full_message += "="*50 + "\n"

full_message += all_results

print(full_message)

# 수집한 텍스트를 KakaoTalk로 보내기
# send_kakao_message(full_message)


# 수집한 텍스트를 메일로 보내기
sender_email = 'lym.coastal@gmail.com'
sender_password = 'oenh ankm dtoj yfsq'
receiver_email = 'leecl2s@hotmail.com'

send_email(full_message, sender_email, sender_password, receiver_email)
