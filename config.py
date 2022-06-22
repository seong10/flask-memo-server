# config 파일 => 환경설정

class Config :
    JWT_SECRET_KEY = 'yhacademy1029##heelo'
                    # 쉽게예측 불가능한 문자열들 / 노출하면 안되는것
    JWT_ACCESS_TOKEN_EXPIRES = False
                            # True 하면 기본적인 시간 (3분?)
                            # False => 시간을 안정함, 계속 유효하게
    PROPAGATE_EXCEPTIONS = True
                    # 헤더에 토큰 없을때 오류표시