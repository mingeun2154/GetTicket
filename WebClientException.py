'''
WebClient에서 발생하는 예외상황들.
'''

class LoginFailedException(Exception):

    def __init__(self, cause):
        if '비밀번호' in cause:
            self.msg = "[로그인 실패] 비밀번호 오류"
        else:
            self.msg = "[로그인 실패] 회원 번호와 비밀번호를 다시 입력해주세요"

    def __str__(self):
        return self.msg

class InvalidStationNameException(Exception):
    def __init__(self, valid_names):
        self.msg = '출발 또는 도착하는 기차역 이름 오류\n유효한 이름은'
    def __str__(self):
        return "출발/도착 역 이름을 확인해주세요"
