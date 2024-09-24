import config
import Helpers

import time
from datetime import datetime

# 실행할 항공편 번호 목록
flight_numbers = ['KE1055', 'KE1515', 'KE1607', 'KE1709', 'OZ8941', 'KE1569', 'BX8183']
passenger_numbers = ['1호차 - 8', '1호차 - 3', '2', '3', '16', '1', '4']

# Flightradar24에서 특정 공항의 도착 페이지 열기
url = 'https://www.flightradar24.com/airport/cju/arrivals'
config.driver.get(url)

# 페이지가 로드될 시간을 대기
time.sleep(2)

# "continue" 버튼 클릭 (쿠키 메시지 처리)
Helpers.click_continue()

# 페이지네이션을 통해 모든 텍스트 수집
Helpers.collect_all_pagination_texts()



# 비행 전후 버튼 클릭
Helpers.prework_button_click()

# 각 항공편 번호에 대해 정보 가져오기
all_results = ""
for i in range(0, len(flight_numbers) , 1) :
    cleaned_flight_number = flight_numbers[i].strip().upper()
    all_results += Helpers.fetch_flight_info(config.driver, cleaned_flight_number, passenger_numbers[i])


# 드라이버 종료
config.driver.quit()

# # 수집한 텍스트 출력
# print( "\n\n\n제주공항 현황\n" + "="*48 )
# formatted_disruptions = format_disruption_texts(disruptions_texts)
# print(formatted_disruptions)

# # 항공편 결과 출력
# print("="*50 + "\n")
# print(all_results)

# 전체 메세지 내용

current_time = datetime.now().strftime('%Y-%m-%d(%a) %H:%M')
full_message = f"\n\n제주공항 현황 : {current_time}\n" + "="*50 + "\n"
formatted_disruptions = Helpers.format_disruption_texts(config.disruptions_texts)
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

Helpers.send_email(full_message, sender_email, sender_password, receiver_email)
