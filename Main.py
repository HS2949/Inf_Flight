import config
import Helpers

import time
import pandas as pd

# CSV 파일에서 항공편 번호 및 인원 정보 불러오기
csv_file_path = 'Plain_Inf.csv'
csv_data = pd.read_csv(csv_file_path)

# 항공편 번호 목록과 인원 정보를 각각 리스트로 변환
flight_numbers = csv_data['항공편'].tolist()
passenger_numbers = csv_data['메모(인원)'].tolist()

# Flightradar24에서 특정 공항의 도착 페이지 열기
config.driver.get(config.url)

# 페이지가 로드될 시간을 대기
time.sleep(2)

# "continue" 버튼 클릭 (쿠키 메시지 처리)
Helpers.click_continue()


# 특정 요소에서 텍스트 가져오기 및 페이지네이션 처리
disruptions_texts = []

# 페이지네이션을 통해 모든 텍스트 수집
Helpers.collect_all_pagination_texts(disruptions_texts)

# 비행 전후 버튼 클릭
Helpers.prework_button_click()


# 각 항공편 번호에 대해 정보 가져오기
all_results = ""
for i in range(0, len(flight_numbers) , 1) :
    cleaned_flight_number = flight_numbers[i].strip().upper()
    #항공편 찾고 드랍 박스 클릭 후 정보 크롤링 후 정보 번역 후 저장
    all_results += Helpers.fetch_flight_info( cleaned_flight_number, passenger_numbers[i])


# 드라이버 종료
config.driver.quit()




# 전체 메세지 내용
full_message = f"\n\n제주공항 현황 : {config.current_time}\n" + "="*50 + "\n"
formatted_disruptions = Helpers.format_disruption_texts(disruptions_texts)

full_message += formatted_disruptions + "\n"
full_message += "="*50 + "\n"
full_message += all_results



print(full_message)


# 수집한 텍스트를 KakaoTalk로 보내기
# send_kakao_message(full_message)

# 수집한 텍스트를 메일로 보내기
Helpers.send_email(full_message, config.sender_email, config.sender_password, config.receiver_email)
