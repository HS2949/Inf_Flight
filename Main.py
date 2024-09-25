import config
import Helpers

import time
from datetime import datetime
import pandas as pd

# CSV 파일에서 항공편 번호 및 인원 정보 불러오기
csv_file_path = "Plain_Inf.csv"
csv_data = pd.read_csv(csv_file_path)

# 항공편 번호 목록과 인원 정보를 각각 리스트로 변환
flight_numbers = csv_data["항공편"].tolist()
passenger_numbers = csv_data["메모(인원)"].tolist()

# Flightradar24에서 특정 공항의 도착 페이지 열기
config.driver.get(config.url)

# 페이지가 로드될 시간을 대기
time.sleep(2)

# "continue" 버튼 클릭 (쿠키 메시지 처리)
Helpers.click_continue()

# 비행 전후 버튼 클릭
Helpers.prework_button_click()


iter_sec = config.set_sec
# 주기적으로 항공편 정보를 수집하는 루프
try:
    while True:
        # 전체 텍스트 : 초기화
        config.full_message = ""
        config.all_Plain_results = []  # 항공정보 변수 초기화

        # 공항 혼잡도 및 정보 가져오기 (페이지네이션)
        Helpers.pagination_work()

        # 각 항공 검색 후 해당  정보 가져오기
        all_Plain_txt = ""  # 항공편 텍스트 초기화
        for i in range(0, len(flight_numbers), 1):
            cleaned_flight_number = flight_numbers[i].strip().upper()
            # 항공편 찾고 드랍 박스 클릭 후 정보 크롤링
            Plain_result = Helpers.fetch_flight_info(
                cleaned_flight_number, passenger_numbers[i]
            )
            # 크롤링한 정보를 텍스트화 : 번역
            Plain_txt = Helpers.text_flight_info(
                cleaned_flight_number, passenger_numbers[i], Plain_result
            )
            all_Plain_txt += Plain_txt

        # 전체 텍스트에 추가 : 항공편 루프 종료 후 넣기
        config.full_message += all_Plain_txt

        # print(config.full_message)

        # 수집한 텍스트를 KakaoTalk로 보내기
        # send_kakao_message(config.full_message)

        # 수집한 텍스트를 메일로 보내기
        Helpers.send_email(
            config.full_message,
            config.sender_email,
            config.sender_password,
            config.receiver_email,
        )

        # iter_min 값에 따라 n분 대기
        # 현재시간 재정의
        config.current_time = datetime.now().strftime("%Y-%m-%d(%a) %H:%M")
        print(
            f"■ Loop : {int(iter_sec / 60)} 분 대기합니다. 현재 시간: {config.current_time}"
        )

        time.sleep(iter_sec)  # 분 단위로 변환하여 대기

except KeyboardInterrupt:
    # 드라이버 종료
    config.driver.quit()
