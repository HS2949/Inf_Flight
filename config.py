# config.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime

# flightradar24 주소
url = "https://www.flightradar24.com/airport/cju/arrivals"

# 현재시간 정의
current_time = datetime.now().strftime("%Y-%m-%d(%a) %H:%M")

# CHECK_INTERVAL 값 (사용자 설정 가능)
CHECK_INTERVAL = 30  # 항공편 정보를 확인하는 간격 (초)
EMAIL_INTERVAL = 30  # 이메일을 보내는 간격 (초, 5분 = 300초)

# 전체 메세지 내용
full_message = f"\n\n제주공항 현황 : {current_time}\n" + "=" * 50 + "\n"


# Chrome 옵션 설정
chrome_options = webdriver.ChromeOptions()

# 창 크기 설정 (optional), # 창 위치 설정 (예: x=200, y=300)
chrome_options.add_argument("window-size=1200,700")
chrome_options.add_argument("window-position=1920,230")

# WebDriver 설정
driver_path = "D:/Py_code/chromedriver.exe"
service = Service(driver_path)
# service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 수집한 텍스트를 메일로 보내기
subject = f"항공기 도착 정보 : {current_time}"
sender_email = "lym.coastal@gmail.com"
sender_password = "oenh ankm dtoj yfsq"
receiver_email = "leecl2s@hotmail.com"


# 주차장 정보 API URL https://www.data.go.kr/data/15056803/openapi.do
parking_url = "http://openapi.airport.co.kr/service/rest/AirportParking/airportparkingRT?serviceKey=DVrkDmVa%2BZW5rqwIvZ2FSN4nL85THjVxlxbGk8QT8Gan5A9ykcS6s9CA1LsCKHWr%2B0Aum%2BLJUgBmrbkMqaSA7w%3D%3D&schAirportCode=CJU"

# key 정보
key_inf = [
    "FROM",
    "SCHEDULED DEPARTURE",
    "ACTUAL DEPARTURE",
    "SCHEDULED ARRIVAL",
    "STATUS",
    "GATE",
    "BAGGAGE BELT",
]

# 정보 수집을 위한 XPath 리스트
xpaths_text = {
    "FROM": f'//*[@id="항공편"]/div[1]/div/div/div[3]/div[1]',
    "SCHEDULED DEPARTURE": f'//*[@id="항공편"]/div[2]/div[1]/div/div[1]/div[2]',
    "ACTUAL DEPARTURE": f'//*[@id="항공편"]/div[2]/div[1]/div/div[2]/div[2]',
    "SCHEDULED ARRIVAL": f'//*[@id="항공편"]/div[2]/div[1]/div/div[3]/div[2]',
    "STATUS": f'//*[@id="항공편"]/div[2]/div[1]/div/div[4]/div[2]',
    "GATE": f'//*[@id="항공편"]/div[2]/div[3]/div[2]/div/div[2]',
    "BAGGAGE BELT": f'//*[@id="항공편"]/div[2]/div[3]/div[3]/div/div[2]',
}

# 한글 번역 딕셔너리
translations = {
    "FROM": "    항공 출발지",
    "SCHEDULED DEPARTURE": "예정 출발 시간",
    "ACTUAL DEPARTURE": "실제 출발 시간",
    "SCHEDULED ARRIVAL": "예정 도착 시간",
    "STATUS": "상태",
    "GATE": "게이트",
    "BAGGAGE BELT": "수하물 벨트",
}
