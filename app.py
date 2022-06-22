from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from config import Config
from resources.follow import FollowListResource, FollowResource
from resources.memo import MemoInfoResource, MemoListResource
from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource, jwt_blacklist

app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 토큰 라이브러리 만들기 
jwt = JWTManager(app)

# 로그아웃된 유저인지 확인하는 함수 작성
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

# 경로와 리소스(API 코드)를 연결한다.
api.add_resource(UserRegisterResource, '/users/register')
api.add_resource(UserLoginResource, '/users/login')
api.add_resource(UserLogoutResource, '/users/logout')

api.add_resource(MemoListResource, '/memo')
api.add_resource(MemoInfoResource, '/memo/<int:memo_id>')

api.add_resource(FollowResource, '/follow/<int:follow_id>')
api.add_resource(FollowListResource, '/follow')


if __name__ == '__main__' :
    app.run()