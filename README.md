# GetTicket
기차표 자동 예매 프로그램

원하는 날짜와 시간대를 저장해놓으면 가장 빠른 열차를 예매해준다.     
**열차 조회 -> 예약 -> 결제 과정이 자동으로 진행**되며 사용자는 카카오페이 결제 요청을 승인하기만 하면 된다.

## Quick Start

1. `WebClient.py`의 reservation info 부분(line# 291 ~ 305) 수정

    example

    ```python
    ############## reservation info ##############
    MEMBER_ID = <srt 페이지 회원 번호>           
    MEMBER_PW = <비밀번호>                       
    DEPT_STATION = '대전'                        
    ARV_STATION = '수서'                         
    TIME_MIN = '10' # 원하는 시간대(최소)
    TIME_MAX = '22' # 원하는 시간대(최대)                         
    MONTH = '4'                                  
    DATE = '7'                                   
    NUM_OF_ADULT = '2'                          
    NUM_OF_CHILD = '0'                          
    SRT_ONLY = True                            
    EXECUTIVE = False                           
    USER_PHONE_NUMBER = <카카오페이 전화번호>   
    USER_BIRTHDAY = <카카오페이 생일>            
    ##############################################
    ```

2. 스크립트 실행
```shell
$ chmod +x WebClient.py
$ ./WebClient.py
```
