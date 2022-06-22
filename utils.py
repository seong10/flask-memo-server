from passlib.hash import pbkdf2_sha256

# 원문 비밀번호를, 암호화 하는 함수
def hash_password(original_password) :
    salt = 'yh*hello12'
    # ex) 1234 => djshe@anjdfnkj$sdj (이상한 문자로 생김)
    # 암호화를 다시 원상복구하는건? => 복구화
    
    # ex) 1234 를 암호화 하면 똑같은 패턴이 나오게된다 
    # 하지만 salt( 공개하지않는 문자열 ) 을 붙이면 섞여서 다른패턴의 문자열이 생긴다
    password = original_password + salt
    password = pbkdf2_sha256.hash(password)
    return password

# 비밀번호가 맞는지 확인하는 함수 , True/ False를 리턴한다
# ex) 1234+salt 를 또다시 암호화 해도 같은 패턴의 문자열이다
def check_password(original_password, hashed_password) :
    salt = 'yh*hello12'
    check = pbkdf2_sha256.verify(original_password+salt, hashed_password)
    return check