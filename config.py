
# config.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime

#flightradar24 주소
url = 'https://www.flightradar24.com/airport/cju/arrivals'

current_time = datetime.now().strftime('%Y-%m-%d(%a) %H:%M')

# WebDriver 설정
driver_path = "D:/Py_code/chromedriver.exe"
service = Service(driver_path)
#service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 수집한 텍스트를 메일로 보내기
sender_email = 'lym.coastal@gmail.com'
sender_password = 'oenh ankm dtoj yfsq'
receiver_email = 'leecl2s@hotmail.com'