
# config.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# WebDriver 설정
#service = ChromeService(executable_path=ChromeDriverManager().install())
#driver = webdriver.Chrome(service=service)
driver_path = "D:/Py_code/chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)


# 특정 요소에서 텍스트 가져오기 및 페이지네이션 처리
disruptions_texts = []