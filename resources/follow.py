from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class FollowResource(Resource) :
    @jwt_required()
    def post(self, follow_id) :
        
        # 1. 클라이언트로부터 데이터를 받아온다.

        user_id = get_jwt_identity()

        # 2. 데이터베이스에 친구정보 인서트한다.
        
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''insert into follow
                    (follower_id, followee_id)
                    values
                    (%s, %s);'''

            record = (user_id, follow_id)

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503
                                        # HTTPStatus.SERVICE_UNAVAILABLE

                                # 200 은 생략되는 200ok
        return {'result' : 'success'}, 200

    @jwt_required()
    def delete(self, follow_id) :
        
        # 1. 클라이언트로 부터 데이터를 받아온다

        user_id = get_jwt_identity()

        # 2. 데이터베이스에 삭제한다.

        try :
            # 데이터 삭제
            # 1. DB에 연결
            connection = get_connection()

            
            # 2. 쿼리문 만들기
            query ='''delete from follow
                where follower_id = %s and followee_id = %s;'''

            record = ( user_id, follow_id )

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다
            # 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야한다
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 503

        return {'result' : 'success'}, 200

class FollowListResource(Resource) :
    
    @jwt_required()
    def get(self) :
        # 1. 클라이언트로부터 데이터 받아온다.
        
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리해준다.
        # request.args 는 딕셔너리다.
        # offset = request.args['offset']
            # 이건 odffset 데이터가 없으면 에러가나고
            # 실무에서 이것을 더 많이씀
        # offset = request.args.get('offset') 
            # 이건 데이터가 없어도 에러가 안남
        offset = request.args['offset']
        limit = request.args['limit']

        ## 유저토큰으로 부터 user_id 반환
        user_id = get_jwt_identity()

        # 2. 디비에서 메모 가져온다.
        # 디비로부터 데이터를 받아서 ,클라이언트에 보내준다.
        try :
            # 데이터 업데이트
            connection = get_connection()

            query = '''select *
                    from memo m
                    join follow f
                    on m.user_id = f.followee_id and follower_id = %s
                    join user u
                    on m.user_id = u.id;
                    limit '''+offset+''', '''+limit+''';'''
            record = (user_id, )

            # select 문은, dictionary = True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            # 실행
            cursor.execute(query, record )

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            result_list = cursor.fetchall()

            print(result_list)

            # 중요! 디비에서 가져온 timestamp 난
            # 파이썬의 datetime 으로 자동 변경된다.
            # json은 datetime 같은게 없다 그냥 문자열이다
            # 문제는! 이 데이터를 json 으로 바로 보낼 수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i = 0
            for record in result_list :
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                result_list[i]['date'] = record['date'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e), 'error_no' : 20}, 503

        return { "result" : "success" ,
            'count' : len(result_list),
            "items" : result_list }, 200