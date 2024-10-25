import time
from datetime import datetime, timedelta

import config
import Helpers

# CSV 파일 읽기
start_time, end_time, flight_numbers, passenger_numbers = Helpers.extract_flight_data()

# 프로그램 시작 시간까지 대기
if datetime.now() < start_time:
    wait_time = (start_time - datetime.now()).total_seconds()
    print(f"  루프 시작까지 약 {wait_time // 60:.0f}분 대기합니다.")
    time.sleep(wait_time)

# 현재 시간이 종료 시간을 넘었으면 종료
if datetime.now() >= end_time:
    print("종료 시간이 되어 프로그램을 종료합니다.")
    raise SystemExit  # 프로그램 종료

# Flightradar24에서 특정 공항의 도착 페이지 열기
config.driver.get(config.url)
time.sleep(2)  # 페이지가 로드될 시간을 대기
Helpers.click_continue()  # "continue" 버튼 클릭 (쿠키 메시지 처리)
Helpers.prework_button_click()  # 비행 전후 버튼 클릭


try:
    while True:
        # 현재 시간이 종료 시간을 넘었으면 종료
        if datetime.now() >= end_time:
            print("종료 시간이 되어 프로그램을 종료합니다.")
            break

        # 전체 텍스트 : 초기화
        config.full_message = ""
        config.all_Plain_results = []  # 항공정보 변수 초기화

        # 현재 시간을 00시 00분 기준으로 초 단위로 변환
        seconds_since_midnight = Helpers.get_seconds_since_midnight()

        # ======================= 이메일 전송
        if seconds_since_midnight % config.EMAIL_INTERVAL == 0:
            print(f"# 이메일 시간 : " + datetime.now().strftime("%Y-%m-%d(%a) %H:%M  %Ss"))

            # 공항 혼잡도 및 정보 가져오기 (페이지네이션)
            Helpers.pagination_work()

            # 항공편 정보 조회
            all_Plain_txt = Helpers.Get_Plain_Data(flight_numbers, passenger_numbers)
            print(f"Get_Plain_Data - 이메일")

            # 전체 텍스트에 추가 : 항공편 루프 종료 후 넣기
            config.full_message += all_Plain_txt
            print(f"이메일 : " + datetime.now().strftime("%Y-%m-%d(%a) %H:%M  %Ss"))
            # 수집한 텍스트를 메일로 보내기
            Helpers.send_email(
                config.full_message,
                config.sender_email,
                config.sender_password,
                config.receiver_email,
            )

        # ======================= 변경 확인 (카카오톡 전송)
        if seconds_since_midnight % config.CHECK_INTERVAL == 0:
            print(f"# 카카오톡 시간 : " + datetime.now().strftime("%Y-%m-%d(%a) %H:%M %Ss"))
            # 항공편 정보 조회 :가져오지 않았을 경우에만 조회  (메일 보내지 않았을 경우)
            if seconds_since_midnight % config.EMAIL_INTERVAL != 0:
                all_Plain_txt = Helpers.Get_Plain_Data(
                    flight_numbers, passenger_numbers
                )
                
            

            print(f"변경확인 : " + datetime.now().strftime("%Y-%m-%d(%a) %H:%M  %Ss"))
            # # 항공편 정보가 변경되었을 경우 카카오톡 알림 전송
            # if flight_info_changed(flight_info):
            #     send_kakao_notification(flight_info)

        # 1초 대기 후 다시 체크
        time.sleep(1)

except KeyboardInterrupt:
    # 드라이버 종료
    config.driver.quit()
