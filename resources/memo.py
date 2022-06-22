from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class MemoListResource(Resource) :
# restful api 의 method 에 해당하는 함수 작성

    @jwt_required()
        ## jwt 토큰부분을 가져와라 인데
        ## header 부분의 토크부분이 없으면 처리를 안해준다
    def post(self) :
        # api 실행 코드를 여기에 작성
        # 실행이 될때 프레임워크가 실행해준다
        
        # 클라이언트에서, body 부분에 작성한 json 을
        # 받아오는 코드
        # {
        #     "title": "커피",
        #     "date": "20220722",
        #     "contents": "커피 마시면서 개발"
        # }
        data = request.get_json()

        ## 유저토큰으로 부터 user_id 반환
        user_id = get_jwt_identity()

        # 받아온 데이터를 DB 저장하면 된다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''insert into memo
                        (title, date, contents, user_id)
                        values
                        ( %s, %s, %s, %s);'''

            record = (data['title'], data['date'], data['contents'], user_id)

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

        print(data)
                                # 200 은 생략되는 200ok
        return {'result' : 'success'}, 200

    @jwt_required()
    def get(self) :
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

        # 디비로부터 데이터를 받아서 ,클라이언트에 보내준다.
        try :
            # 데이터 업데이트
            connection = get_connection()

            query = ''' select *
                    from memo
                    where user_id = %s
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

class MemoInfoResource(Resource) :
    @jwt_required()
    def put(self, memo_id) :
                # app.py에 설정한
                # 경로 때문에 memo_id 작성
        
        # body에서 전달된 데이터를 처리
        # {
        #     "title": "점심먹기",
        #     "date" : "2022-03-14",
        #     "contents": "짜장면"
        # }
        data = request.get_json()

        user_id = get_jwt_identity()
        
        # 디비 업데이트 실행코드
        try :
            # 데이터 업데이트
            # 1. DB에 연결
            connection = get_connection()

            ### 먼저 recipe_id 에 들어있는 user_id가
            ### 이 사람인지 먼저 확인한다.

            query = '''select user_id
                        from memo
                        where id = %s;'''
            record = (memo_id ,)
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            ### 추가 예외처리
            # if len(result_list) == 0 :
            #     cursor.close()
            #     connection.close()
            #     return {'error' : '레시피 아이디가 잘못되었습니다.'}, 400

            memo = result_list[0]

            if memo['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {'error' : '남의 레시피를 수정할 수 없습니다.'}, 401


            ### 여기까지 토큰적용을 위한 추가코드


            # 2. 쿼리문 만들기
            query ='''update memo
                    set title = %s,
                    date = %s,
                    contents = %s
                    where id = %s and user_id = %s;'''

            record = (data['title'],
                        data['date'],
                        data['contents'],
                        memo_id, user_id )

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

    # 삭제하는 delete 함수
    @jwt_required()
    def delete(self, memo_id) :
               
        # 1. 클라이언트로 부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. 디비로부터 메모를 삭제한다
        try :
            # 데이터 삭제
            # 1. DB에 연결
            connection = get_connection()

            
            # 2. 쿼리문 만들기
            query ='''delete from memo
                    where id = %s and user_id = %s;'''

            record = ( memo_id, user_id )

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
